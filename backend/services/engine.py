"""
Rule-based recommendation engine for BioLoop Gujarat.
Operates on village-level origins with catchment radius filtering.
NO ML, NO LLM calls. Deterministic, transparent, and auditable.
"""
import json
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from models import BiomassType, Pathway, Offtaker, LogisticsHub, FarmerGroup, Weight, Village, District
from services.geo import haversine_distance, estimate_trip_time_minutes

# Catchment radius default in kilometers
DEFAULT_CATCHMENT_RADIUS_KM = 100.0

VERIFICATION_CHECKLISTS = {
    "briquetting": [
        "Conduct lab proximate analysis (ASTM D3172 or IS 1350) for total moisture, ash content, and volatile matter.",
        "Obtain bulk density measurement to verify road transport payload economics (target >120 kg/m³ loose).",
        "Confirm off-taker press type (piston vs screw press requires different particle size <8mm).",
        "Inspect seasonal storage protection from monsoon humidity to prevent swelling."
    ],
    "pellet_production": [
        "Verify raw material silica / sand content from field collection (silica >2% accelerates pellet die wear).",
        "Confirm moisture levels strictly stay below 12-14% at mill intake, or factor rotary dryer fuel costs.",
        "Sample pellet durability index (PDI) with local test press to ensure transport stability.",
        "Verify industrial boiler co-firing emission norms (CPCB / GPCB particulate compliance)."
    ],
    "biochar": [
        "Analyze feedstock lignin-to-cellulose ratio to estimate fixed carbon yield (typical 25-35%).",
        "Determine kiln/pyrolysis unit emissions clearance with Gujarat Pollution Control Board (GPCB).",
        "Test heavy metal content (As, Cd, Pb) before certifying for agricultural soil amendment.",
        "Establish local farmer field trial protocol for application rates (5 to 10 t/ha)."
    ],
    "activated_carbon": [
        "Perform iodine number and methylene blue adsorption testing on trial activated sample.",
        "Verify fixed carbon and low ash (<5%) suitability for chemical or steam activation.",
        "Check plant minimum throughput contract requirements (typically continuous 500+ t/month).",
        "Confirm proximity to effluent treatment / water supply for chemical washing stages."
    ],
    "composting": [
        "Calculate Carbon-to-Nitrogen (C:N) ratio; plan co-substrates (e.g., dairy manure / pressmud).",
        "Confirm windrow pad drainage and leachate management according to Solid Waste Management Rules.",
        "Assess seasonal moisture addition needs during hot Saurashtra / North Gujarat summer months.",
        "Test final compost batch against Fertilizer Control Order (FCO) quality standards."
    ]
}


def load_weights_from_db_or_config(db: Session) -> Dict[str, float]:
    """Retrieve weights from the DB, fallback to default 1.0 sum."""
    weights_rows = db.query(Weight).all()
    if weights_rows and len(weights_rows) >= 5:
        return {w.key: w.value for w in weights_rows}
    return {
        "w1_material_fit": 0.30,
        "w2_processing_fit": 0.20,
        "w3_logistics": 0.20,
        "w4_market_fit": 0.15,
        "w5_ease": 0.15
    }


def evaluate_eligibility(
    biomass: BiomassType,
    pathway: Pathway,
    quantity: float,
    moisture_content: float | None
) -> Tuple[bool, List[str], bool]:
    """
    Step A: Hard rules filter.
    Returns (eligible, reasons, requires_drying_flag)
    """
    reasons = []
    requires_drying = False

    # Rule 1: Biomass compatibility
    try:
        compatible_ids = json.loads(pathway.compatible_biomass_ids)
    except Exception:
        compatible_ids = []

    if biomass.id not in compatible_ids:
        reasons.append(
            f"Biomass '{biomass.name}' is not in the validated feedstock list for {pathway.name} "
            f"(physical/lignocellulosic mismatch)."
        )

    # Rule 2: Minimum viable volume threshold
    if quantity < pathway.min_quantity_tpm:
        reasons.append(
            f"Quantity ({quantity:.1f} t/month) is below the minimum viable operating scale "
            f"of {pathway.min_quantity_tpm:.1f} t/month for {pathway.name}."
        )

    # Rule 3: Moisture tolerance
    if moisture_content is not None:
        if moisture_content > pathway.max_moisture:
            excess = moisture_content - pathway.max_moisture
            if excess > 25.0:
                reasons.append(
                    f"Moisture content ({moisture_content:.1f}%) far exceeds maximum pathway tolerance "
                    f"({pathway.max_moisture:.1f}%). Pre-drying is energetically and economically non-viable."
                )
            else:
                requires_drying = True

    eligible = len(reasons) == 0
    return eligible, reasons, requires_drying


def calculate_data_confidence(
    biomass: BiomassType,
    pathway: Pathway,
    moisture_provided: bool,
    seasonality_provided: bool,
    nearest_offtaker_distance: float | None
) -> Tuple[str, List[str]]:
    """
    Determine confidence level: High, Moderate, or Low.
    Track missing fields explicitly.
    """
    missing_info = []
    points = 0

    if moisture_provided:
        points += 1
    else:
        missing_info.append("Feedstock moisture content was not provided (default baseline assumed).")

    if seasonality_provided:
        points += 1
    else:
        missing_info.append("Seasonality / harvesting schedule notes are missing.")

    if nearest_offtaker_distance is not None:
        points += 1
    else:
        missing_info.append("No active registered off-takers found within direct geographic threshold.")

    if biomass.record_status == "verified":
        points += 1
    else:
        missing_info.append(f"Biomass specification for '{biomass.name}' relies on illustrative demo data.")

    if pathway.record_status == "verified":
        points += 1
    else:
        missing_info.append(f"Pathway operational thresholds for '{pathway.name}' rely on demo heuristics.")

    if points >= 4:
        confidence = "High"
    elif points >= 2:
        confidence = "Moderate"
    else:
        confidence = "Low"

    return confidence, missing_info


def calculate_factor_scores(
    biomass: BiomassType,
    pathway: Pathway,
    quantity: float,
    moisture_content: float | None,
    requires_drying: bool,
    nearest_offtaker_km: float | None,
    nearest_trip_time_mins: int | None,
    weights: Dict[str, float]
) -> List[Dict[str, Any]]:
    """
    Calculate 5 individual factor scores (0-100) and weighted contributions.
    """
    factors = []

    # 1. Material Fit (0-100)
    material_score = 85.0 if biomass.id == "groundnut_shell" else (78.0 if biomass.id == "cotton_stalk" else 72.0)
    if pathway.id in ["briquetting", "pellet_production"] and biomass.id == "groundnut_shell":
        material_score = 94.0
    elif pathway.id == "biochar" and biomass.id == "cotton_stalk":
        material_score = 88.0
    elif pathway.id == "composting" and biomass.id == "bagasse":
        material_score = 86.0

    w1 = weights.get("w1_material_fit", 0.30)
    factors.append({
        "factor_name": "Material Compatibility",
        "raw_score": material_score,
        "weight": w1,
        "weighted_score": round(material_score * w1, 1),
        "status": "Verified" if biomass.record_status == "verified" else "Illustrative",
        "explanation": (
            f"{biomass.name} characteristics align with {pathway.name} technical parameters. "
            f"Lignocellulosic density and calorific yield fall within standard processing limits."
        )
    })

    # 2. Processing Fit (0-100)
    if moisture_content is None:
        proc_score = 70.0
        status_proc = "Requires verification"
        proc_exp = (
            f"Moisture was not specified. Estimated assuming standard {biomass.typical_moisture_min:.0f}-{biomass.typical_moisture_max:.0f}%. "
            f"Operational energy balance requires moisture testing at intake."
        )
    elif requires_drying:
        excess = moisture_content - pathway.max_moisture
        proc_score = max(35.0, 85.0 - (excess * 3.5))
        status_proc = "Requires verification"
        proc_exp = (
            f"Moisture ({moisture_content:.1f}%) exceeds maximum tolerance ({pathway.max_moisture:.1f}%). "
            f"Requires pre-treatment drying step ({excess:.1f}% reduction needed), which incurs thermal energy cost."
        )
    else:
        proc_score = 92.0
        status_proc = "Verified"
        proc_exp = (
            f"Moisture ({moisture_content:.1f}%) is well within the {pathway.max_moisture:.1f}% ceiling for {pathway.name}. "
            f"Direct intake without dedicated pre-drying stage."
        )

    w2 = weights.get("w2_processing_fit", 0.20)
    factors.append({
        "factor_name": "Processing Requirements",
        "raw_score": round(proc_score, 1),
        "weight": w2,
        "weighted_score": round(proc_score * w2, 1),
        "status": status_proc,
        "explanation": proc_exp
    })

    # 3. Location and Logistics (0-100)
    w3 = weights.get("w3_logistics", 0.20)
    if nearest_offtaker_km is None:
        logistics_score = 35.0
        logistics_exp = "No designated off-takers found within catchment radius. Cross-district transit will be required."
        log_status = "Requires verification"
    elif nearest_offtaker_km <= 20.0:
        logistics_score = 96.0
        trip_str = f" (~{nearest_trip_time_mins} mins one-way tractor transit)" if nearest_trip_time_mins else ""
        logistics_exp = f"Nearest matched facility is only ~{nearest_offtaker_km:.1f} km away{trip_str}. Highly favorable trucking radius."
        log_status = "Illustrative"
    elif nearest_offtaker_km <= 50.0:
        logistics_score = 86.0
        trip_str = f" (~{nearest_trip_time_mins} mins one-way tractor transit)" if nearest_trip_time_mins else ""
        logistics_exp = f"Nearest matched facility is ~{nearest_offtaker_km:.1f} km away{trip_str}. Viable for direct tractor-trolley or 10-wheel transport."
        log_status = "Illustrative"
    elif nearest_offtaker_km <= 90.0:
        logistics_score = 68.0
        trip_str = f" (~{nearest_trip_time_mins} mins one-way transit)" if nearest_trip_time_mins else ""
        logistics_exp = f"Nearest matched facility is ~{nearest_offtaker_km:.1f} km away{trip_str}. Freight haulage will represent 15-25% of delivered biomass value."
        log_status = "Illustrative"
    else:
        logistics_score = max(25.0, 100.0 - (nearest_offtaker_km * 0.45))
        trip_str = f" (~{nearest_trip_time_mins} mins one-way transit)" if nearest_trip_time_mins else ""
        logistics_exp = f"Nearest facility is distant (~{nearest_offtaker_km:.1f} km{trip_str}). Centralized aggregation hub transfer is recommended."
        log_status = "Requires verification"

    factors.append({
        "factor_name": "Location & Logistics",
        "raw_score": round(logistics_score, 1),
        "weight": w3,
        "weighted_score": round(logistics_score * w3, 1),
        "status": log_status,
        "explanation": logistics_exp
    })

    # 4. Market Fit (0-100)
    w4 = weights.get("w4_market_fit", 0.15)
    market_scores = {
        "briquetting": (88.0, "High domestic demand from Saurashtra ceramic, edible oil, and textile processing boilers replacing coal."),
        "pellet_production": (84.0, "Steady co-firing demand from coal-fired thermal plants mandated by government co-firing policies."),
        "biochar": (66.0, "Emerging soil amendment demand among horticulture & regenerative agriculture farms; premium voluntary carbon credit markets."),
        "activated_carbon": (74.0, "High-value export and industrial effluent treatment filtration demand, but requires strict quality consistency."),
        "composting": (78.0, "Established regional agronomic market in Gujarat for organic fertilizer, high seasonal demand during sowing.")
    }
    m_score, m_exp = market_scores.get(pathway.id, (70.0, "Moderate regional market interest."))
    factors.append({
        "factor_name": "Market Fit & Demand",
        "raw_score": m_score,
        "weight": w4,
        "weighted_score": round(m_score * w4, 1),
        "status": "Illustrative",
        "explanation": m_exp
    })

    # 5. Ease & Capex (0-100)
    w5 = weights.get("w5_ease", 0.15)
    ease_scores = {
        "briquetting": (82.0, "Proven mechanized technology with low-to-medium capex and readily available domestic machinery manufacturers."),
        "pellet_production": (68.0, "Medium capex; requires die maintenance, hammer milling, and strict conditioning moisture control."),
        "biochar": (62.0, "Moderate capex for continuous pyrolyzers; simpler for top-lit updraft (TLUD) artisanal kilns but lower throughput."),
        "activated_carbon": (42.0, "High capex chemical/steam activation kilns, complex air emissions controls, and high technical oversight."),
        "composting": (86.0, "Low capex open-windrow or static pile composting; straightforward operational deployment.")
    }
    e_score, e_exp = ease_scores.get(pathway.id, (65.0, "Moderate deployment ease."))
    factors.append({
        "factor_name": "Ease & Capital Intensity",
        "raw_score": e_score,
        "weight": w5,
        "weighted_score": round(e_score * w5, 1),
        "status": "Illustrative",
        "explanation": e_exp
    })

    return factors


def run_evaluation(
    db: Session,
    biomass_id: str,
    village_id: str,
    quantity: float,
    moisture_content: float | None = None,
    seasonality_notes: str | None = None,
    max_radius_km: float = DEFAULT_CATCHMENT_RADIUS_KM
) -> Dict[str, Any]:
    """
    Main village-level evaluation pipeline:
    1. Look up origin village coordinates
    2. Filter offtakers, hubs, and farmer groups within max_radius_km
    3. Evaluate eligibility and calculate weighted factor scores
    4. Compile deterministic explanations and confidence scores
    """
    biomass = db.query(BiomassType).filter(BiomassType.id == biomass_id).first()
    if not biomass:
        raise ValueError(f"Biomass type '{biomass_id}' not found.")

    village = db.query(Village).filter(Village.id == village_id).first()
    if not village:
        raise ValueError(f"Village '{village_id}' not found.")

    district = db.query(District).filter(District.id == village.district_id).first()
    district_name = district.name if district else "Gujarat"

    user_lat = village.lat
    user_lng = village.lng

    weights = load_weights_from_db_or_config(db)
    all_pathways = db.query(Pathway).all()
    all_offtakers = db.query(Offtaker).all()
    all_hubs = db.query(LogisticsHub).all()
    all_farmer_groups = db.query(FarmerGroup).all()

    # Villages map for quick lookup of location names
    village_map = {v.id: v for v in db.query(Village).all()}
    district_map = {d.id: d for d in db.query(District).all()}

    # Calculate distances for Offtakers
    nearby_offtakers = []
    for off in all_offtakers:
        dist = haversine_distance(user_lat, user_lng, off.lat, off.lng)
        trip_time = estimate_trip_time_minutes(dist)
        try:
            accepts_bio = json.loads(off.accepts_biomass_ids)
            serves_paths = json.loads(off.pathway_ids)
        except Exception:
            accepts_bio, serves_paths = [], []

        v_entity = village_map.get(off.village_id)
        d_entity = district_map.get(v_entity.district_id) if v_entity else None

        # Filter by biomass compatibility and catchment radius
        if biomass.id in accepts_bio and dist <= max_radius_km:
            nearby_offtakers.append({
                "id": off.id,
                "name": off.name,
                "type": off.type,
                "village_id": off.village_id,
                "village_name": v_entity.name if v_entity else off.village_id,
                "district_name": d_entity.name if d_entity else "Gujarat",
                "lat": off.lat,
                "lng": off.lng,
                "accepts_biomass_ids": accepts_bio,
                "pathway_ids": serves_paths,
                "capacity_tpm": off.capacity_tpm,
                "listing_status": off.listing_status,
                "source": off.source,
                "limitations": off.limitations,
                "record_status": off.record_status,
                "distance_km": dist,
                "est_trip_time_mins": trip_time
            })

    nearby_offtakers.sort(key=lambda x: x["distance_km"])

    # Calculate distances for Logistics Hubs
    nearby_hubs = []
    for hub in all_hubs:
        dist = haversine_distance(user_lat, user_lng, hub.lat, hub.lng)
        trip_time = estimate_trip_time_minutes(dist)
        v_entity = village_map.get(hub.village_id)
        d_entity = district_map.get(v_entity.district_id) if v_entity else None

        if dist <= max_radius_km:
            nearby_hubs.append({
                "id": hub.id,
                "name": hub.name,
                "village_id": hub.village_id,
                "village_name": v_entity.name if v_entity else hub.village_id,
                "district_name": d_entity.name if d_entity else "Gujarat",
                "lat": hub.lat,
                "lng": hub.lng,
                "hub_type": hub.hub_type,
                "listing_status": hub.listing_status,
                "source": hub.source,
                "limitations": hub.limitations,
                "record_status": hub.record_status,
                "distance_km": dist,
                "est_trip_time_mins": trip_time
            })
    nearby_hubs.sort(key=lambda x: x["distance_km"])

    # Calculate distances for Farmer Producer Groups
    nearby_farmer_groups = []
    for fg in all_farmer_groups:
        v_entity = village_map.get(fg.village_id)
        d_entity = district_map.get(v_entity.district_id) if v_entity else None
        fg_lat = v_entity.lat if v_entity else user_lat
        fg_lng = v_entity.lng if v_entity else user_lng
        dist = haversine_distance(user_lat, user_lng, fg_lat, fg_lng)

        try:
            b_ids = json.loads(fg.biomass_ids)
            season_m = json.loads(fg.season_months_json)
        except Exception:
            b_ids, season_m = [], []

        if biomass.id in b_ids and dist <= max_radius_km:
            nearby_farmer_groups.append({
                "id": fg.id,
                "name": fg.name,
                "village_id": fg.village_id,
                "village_name": v_entity.name if v_entity else fg.village_id,
                "district_name": d_entity.name if d_entity else "Gujarat",
                "lat": fg_lat,
                "lng": fg_lng,
                "biomass_ids": b_ids,
                "est_supply_tpm": fg.est_supply_tpm,
                "season_months": season_m,
                "source": fg.source,
                "limitations": fg.limitations,
                "record_status": fg.record_status,
                "distance_km": dist
            })
    nearby_farmer_groups.sort(key=lambda x: x["distance_km"])

    # Evaluate Pathways
    ranked_pathways = []
    all_missing_info = set()

    for path in all_pathways:
        eligible, inelig_reasons, requires_drying = evaluate_eligibility(
            biomass=biomass,
            pathway=path,
            quantity=quantity,
            moisture_content=moisture_content
        )

        path_offtakers = [o for o in nearby_offtakers if path.id in o["pathway_ids"]]
        nearest_dist = path_offtakers[0]["distance_km"] if path_offtakers else None
        nearest_trip = path_offtakers[0]["est_trip_time_mins"] if path_offtakers else None

        factors = calculate_factor_scores(
            biomass=biomass,
            pathway=path,
            quantity=quantity,
            moisture_content=moisture_content,
            requires_drying=requires_drying,
            nearest_offtaker_km=nearest_dist,
            nearest_trip_time_mins=nearest_trip,
            weights=weights
        )

        confidence, path_missing = calculate_data_confidence(
            biomass=biomass,
            pathway=path,
            moisture_provided=(moisture_content is not None),
            seasonality_provided=bool(seasonality_notes and seasonality_notes.strip()),
            nearest_offtaker_distance=nearest_dist
        )
        for m in path_missing:
            all_missing_info.add(m)

        if eligible:
            total_score = round(sum(f["weighted_score"] for f in factors), 1)
            if nearest_dist is not None and nearest_dist <= 25.0:
                short_reason = f"Strong material fit with local off-taker only ~{nearest_dist:.1f} km away (~{nearest_trip} mins estimate)."
            elif nearest_dist is not None and nearest_dist <= max_radius_km:
                short_reason = f"Compatible technical fit; logistics within catchment radius (~{nearest_dist:.1f} km, ~{nearest_trip} mins estimate)."
            elif requires_drying:
                short_reason = f"Viable pathway, but requires pre-treatment drying to meet {path.max_moisture:.0f}% moisture threshold."
            else:
                short_reason = f"Compatible technical fit; no off-takers within {max_radius_km:.0f} km catchment radius."
        else:
            total_score = 0.0
            short_reason = f"Excluded: {inelig_reasons[0]}"

        logistics_level = (
            f"Local (<25 km, ~{nearest_trip or 30}m)" if (nearest_dist and nearest_dist <= 25)
            else (f"Catchment (25-70 km, ~{nearest_trip or 90}m)" if (nearest_dist and nearest_dist <= 70)
                  else (f"Sub-regional (70-{max_radius_km:.0f} km)" if (nearest_dist and nearest_dist <= max_radius_km)
                        else "No local offtakers in radius"))
        )
        market_fit_level = "High" if path.id in ["briquetting", "pellet_production"] else ("Moderate" if path.id in ["composting", "activated_carbon"] else "Developing")

        ranked_pathways.append({
            "pathway_id": path.id,
            "pathway_name": path.name,
            "score": total_score,
            "rank": 0,
            "eligible": eligible,
            "status_reason": short_reason,
            "capex_level": path.capex_level,
            "ease_level": path.ease_level,
            "logistics_level": logistics_level,
            "market_fit_level": market_fit_level,
            "data_confidence": confidence,
            "factors": factors,
            "ineligibility_reasons": inelig_reasons,
            "verification_steps": VERIFICATION_CHECKLISTS.get(path.id, [
                "Verify feedstock sample characteristics with regional test laboratory.",
                "Inspect local off-taker operational availability and pricing terms."
            ]),
            "source": path.source,
            "limitations": path.limitations,
            "record_status": path.record_status
        })

    eligible_list = [p for p in ranked_pathways if p["eligible"]]
    ineligible_list = [p for p in ranked_pathways if not p["eligible"]]

    eligible_list.sort(key=lambda x: x["score"], reverse=True)
    for idx, p in enumerate(eligible_list, start=1):
        p["rank"] = idx

    ineligible_list.sort(key=lambda x: x["pathway_name"])
    for idx, p in enumerate(ineligible_list, start=len(eligible_list) + 1):
        p["rank"] = idx

    combined_ranked = eligible_list + ineligible_list

    return {
        "input_summary": {
            "biomass_id": biomass.id,
            "biomass_name": biomass.name,
            "biomass_category": biomass.category,
            "district_id": district.id if district else "",
            "district_name": district_name,
            "village_id": village.id,
            "village_name": village.name,
            "taluka": village.taluka,
            "village_lat": village.lat,
            "village_lng": village.lng,
            "quantity_tpm": quantity,
            "moisture_content_pct": moisture_content,
            "seasonality_notes": seasonality_notes
        },
        "ranked_pathways": combined_ranked,
        "eligible_count": len(eligible_list),
        "ineligible_count": len(ineligible_list),
        "nearby_offtakers": nearby_offtakers,
        "nearby_hubs": nearby_hubs,
        "nearby_farmer_groups": nearby_farmer_groups,
        "missing_info": sorted(list(all_missing_info)),
        "catchment_radius_km": max_radius_km,
        "disclaimer": "A recommendation is not a guaranteed transaction. Verify with local participants."
    }
