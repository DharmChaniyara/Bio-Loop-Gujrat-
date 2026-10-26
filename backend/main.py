"""
FastAPI application for BioLoop Gujarat.
Village-level granularity with catchment radius calculations.
"""
import json
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from db import get_db, Base, engine
from seed import seed_database
import models
import schemas
from services.engine import run_evaluation, DEFAULT_CATCHMENT_RADIUS_KM
from services.geo import haversine_distance, estimate_trip_time_minutes

# Ensure schema and initial seed data exist
Base.metadata.create_all(bind=engine)
seed_database()

app = FastAPI(
    title="BioLoop Gujarat API",
    description="Deterministic decision-support engine for agricultural biomass utilization at village level in Gujarat.",
    version="2.0.0"
)

# Enable CORS for Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "BioLoop Gujarat Backend",
        "engine": "Rules-based deterministic engine",
        "granularity": "Village / Taluka level",
        "llm_calls": 0,
        "ml_models": 0
    }


@app.get("/api/districts", response_model=List[schemas.DistrictOut], tags=["Geography"])
def get_districts(db: Session = Depends(get_db)):
    """Retrieve all Gujarat districts with coordinates."""
    return db.query(models.District).order_by(models.District.name).all()


@app.get("/api/villages", response_model=List[schemas.VillageOut], tags=["Geography"])
def get_villages(
    district_id: Optional[str] = Query(None, description="Filter by district ID"),
    db: Session = Depends(get_db)
):
    """Retrieve villages/talukas, optionally filtered by district_id."""
    query = db.query(models.Village)
    if district_id:
        query = query.filter(models.Village.district_id == district_id.strip().lower())
    villages = query.order_by(models.Village.name).all()

    results = []
    for v in villages:
        try:
            crops = json.loads(v.primary_crops_json) if v.primary_crops_json else []
        except Exception:
            crops = []
        results.append(schemas.VillageOut(
            id=v.id,
            name=v.name,
            taluka=v.taluka,
            district_id=v.district_id,
            lat=v.lat,
            lng=v.lng,
            coord_precision=v.coord_precision,
            primary_crops_json=v.primary_crops_json,
            primary_crops=crops,
            source=v.source,
            limitations=v.limitations,
            record_status=v.record_status
        ))
    return results


@app.get("/api/biomass-types", response_model=List[schemas.BiomassTypeOut], tags=["Feedstock"])
def get_biomass_types(db: Session = Depends(get_db)):
    """Retrieve available biomass types and moisture tolerances."""
    types = db.query(models.BiomassType).all()
    results = []
    for b in types:
        try:
            months = json.loads(b.harvest_months_json) if b.harvest_months_json else []
        except Exception:
            months = []
        results.append(schemas.BiomassTypeOut(
            id=b.id,
            name=b.name,
            category=b.category,
            typical_moisture_min=b.typical_moisture_min,
            typical_moisture_max=b.typical_moisture_max,
            harvest_months=months,
            properties_json=b.properties_json,
            source=b.source,
            limitations=b.limitations,
            record_status=b.record_status
        ))
    return results


@app.get("/api/offtakers", response_model=List[schemas.OfftakerOut], tags=["Facilities"])
def get_offtakers(
    village_id: Optional[str] = Query(None, description="Origin village ID for distance calculation"),
    pathway: Optional[str] = Query(None, description="Filter by pathway ID"),
    radius_km: Optional[float] = Query(None, description="Max catchment radius filter in km"),
    db: Session = Depends(get_db)
):
    """Retrieve offtakers with optional village origin distance and pathway filtering."""
    origin_village = None
    if village_id:
        origin_village = db.query(models.Village).filter(models.Village.id == village_id).first()

    query = db.query(models.Offtaker)
    raw_offtakers = query.all()

    # Preload names
    village_map = {v.id: v for v in db.query(models.Village).all()}
    district_map = {d.id: d for d in db.query(models.District).all()}

    filtered = []
    for o in raw_offtakers:
        try:
            accepts_bio = json.loads(o.accepts_biomass_ids)
            serves_paths = json.loads(o.pathway_ids)
        except Exception:
            accepts_bio, serves_paths = [], []

        if pathway and pathway not in serves_paths:
            continue

        dist = None
        trip_time = None
        if origin_village:
            dist = haversine_distance(origin_village.lat, origin_village.lng, o.lat, o.lng)
            trip_time = estimate_trip_time_minutes(dist)
            if radius_km and dist > radius_km:
                continue

        v_ent = village_map.get(o.village_id)
        d_ent = district_map.get(v_ent.district_id) if v_ent else None

        filtered.append(schemas.OfftakerOut(
            id=o.id,
            name=o.name,
            type=o.type,
            village_id=o.village_id,
            village_name=v_ent.name if v_ent else o.village_id,
            district_name=d_ent.name if d_ent else "Gujarat",
            lat=o.lat,
            lng=o.lng,
            accepts_biomass_ids=accepts_bio,
            pathway_ids=serves_paths,
            capacity_tpm=o.capacity_tpm,
            listing_status=o.listing_status,
            source=o.source,
            limitations=o.limitations,
            record_status=o.record_status,
            distance_km=dist,
            est_trip_time_mins=trip_time
        ))

    if origin_village:
        filtered.sort(key=lambda x: x.distance_km if x.distance_km is not None else 9999)

    return filtered


@app.get("/api/hubs", response_model=List[schemas.LogisticsHubOut], tags=["Facilities"])
def get_logistics_hubs(
    village_id: Optional[str] = Query(None, description="Origin village ID"),
    radius_km: Optional[float] = Query(None, description="Max radius filter in km"),
    db: Session = Depends(get_db)
):
    """Retrieve logistics hubs with optional origin distance filtering."""
    origin_village = None
    if village_id:
        origin_village = db.query(models.Village).filter(models.Village.id == village_id).first()

    raw_hubs = db.query(models.LogisticsHub).all()
    village_map = {v.id: v for v in db.query(models.Village).all()}
    district_map = {d.id: d for d in db.query(models.District).all()}

    results = []
    for h in raw_hubs:
        dist = None
        trip_time = None
        if origin_village:
            dist = haversine_distance(origin_village.lat, origin_village.lng, h.lat, h.lng)
            trip_time = estimate_trip_time_minutes(dist)
            if radius_km and dist > radius_km:
                continue

        v_ent = village_map.get(h.village_id)
        d_ent = district_map.get(v_ent.district_id) if v_ent else None

        results.append(schemas.LogisticsHubOut(
            id=h.id,
            name=h.name,
            village_id=h.village_id,
            village_name=v_ent.name if v_ent else h.village_id,
            district_name=d_ent.name if d_ent else "Gujarat",
            lat=h.lat,
            lng=h.lng,
            hub_type=h.hub_type,
            listing_status=h.listing_status,
            source=h.source,
            limitations=h.limitations,
            record_status=h.record_status,
            distance_km=dist,
            est_trip_time_mins=trip_time
        ))

    if origin_village:
        results.sort(key=lambda x: x.distance_km if x.distance_km is not None else 9999)

    return results


@app.get("/api/farmer-groups", response_model=List[schemas.FarmerGroupOut], tags=["Feedstock"])
def get_farmer_groups(
    village_id: Optional[str] = Query(None, description="Origin village ID"),
    radius_km: Optional[float] = Query(None, description="Max radius filter in km"),
    db: Session = Depends(get_db)
):
    """Retrieve farmer groups with optional distance from village origin."""
    origin_village = None
    if village_id:
        origin_village = db.query(models.Village).filter(models.Village.id == village_id).first()

    raw_groups = db.query(models.FarmerGroup).all()
    village_map = {v.id: v for v in db.query(models.Village).all()}
    district_map = {d.id: d for d in db.query(models.District).all()}

    results = []
    for fg in raw_groups:
        try:
            b_ids = json.loads(fg.biomass_ids)
            season_m = json.loads(fg.season_months_json)
        except Exception:
            b_ids, season_m = [], []

        v_ent = village_map.get(fg.village_id)
        d_ent = district_map.get(v_ent.district_id) if v_ent else None
        fg_lat = v_ent.lat if v_ent else (origin_village.lat if origin_village else 22.0)
        fg_lng = v_ent.lng if v_ent else (origin_village.lng if origin_village else 71.0)

        dist = None
        if origin_village:
            dist = haversine_distance(origin_village.lat, origin_village.lng, fg_lat, fg_lng)
            if radius_km and dist > radius_km:
                continue

        results.append(schemas.FarmerGroupOut(
            id=fg.id,
            name=fg.name,
            village_id=fg.village_id,
            village_name=v_ent.name if v_ent else fg.village_id,
            district_name=d_ent.name if d_ent else "Gujarat",
            lat=fg_lat,
            lng=fg_lng,
            biomass_ids=b_ids,
            est_supply_tpm=fg.est_supply_tpm,
            season_months=season_m,
            source=fg.source,
            limitations=fg.limitations,
            record_status=fg.record_status,
            distance_km=dist
        ))

    if origin_village:
        results.sort(key=lambda x: x.distance_km if x.distance_km is not None else 9999)

    return results


@app.get("/api/weights", response_model=List[schemas.WeightItem], tags=["Evaluation"])
def get_weights(db: Session = Depends(get_db)):
    """Retrieve evaluation weights."""
    return db.query(models.Weight).all()


@app.put("/api/weights", response_model=List[schemas.WeightItem], tags=["Evaluation"])
def update_weights(req: schemas.WeightsUpdateRequest, db: Session = Depends(get_db)):
    """Update evaluation weights (must sum to 1.0)."""
    for k, v in req.weights.items():
        w_row = db.query(models.Weight).filter(models.Weight.key == k).first()
        if w_row:
            w_row.value = round(v, 4)
    db.commit()
    return db.query(models.Weight).all()


@app.post("/api/evaluate", response_model=schemas.EvaluationResponse, tags=["Evaluation"])
def evaluate_biomass(req: schemas.EvaluateRequest, db: Session = Depends(get_db)):
    """
    Run village-origin evaluation:
    1. Origin coordinates from village_id
    2. Hard-rule eligibility filter
    3. Multi-factor weighted ranking
    4. Proximity & estimated transit times to offtakers, hubs, and farmer groups within max_radius_km
    5. Deterministic explanation templates and confidence scoring
    """
    try:
        max_r = req.max_radius_km if req.max_radius_km else DEFAULT_CATCHMENT_RADIUS_KM
        result = run_evaluation(
            db=db,
            biomass_id=req.biomass_type,
            village_id=req.village_id,
            quantity=req.quantity,
            moisture_content=req.moisture_content,
            seasonality_notes=req.seasonality_notes,
            max_radius_km=max_r
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation error: {str(e)}"
        )
