"""
Unit tests and scenario tests for BioLoop Gujarat (Village-level evaluation).
Tests:
1. Eligibility filter (hard rules)
2. Scoring calculations and weights summing to 1.0
3. Haversine distance accuracy & estimated trip times
4. Catchment radius filtering
5. The 5 Scenarios:
   - Scenario 1: Groundnut shells / Talaja (Bhavnagar) / 120 t/mo / 11% moisture
   - Scenario 2: Cotton stalks / Limbdi / high moisture (48%)
   - Scenario 3: Very small quantity (5 t/mo below min viability thresholds)
   - Scenario 4: Input with missing moisture (confidence and explanation verification)
   - Scenario 5: Village with no off-takers inside narrow radius (returns helpful empty state, no crash)
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from db import SessionLocal
from models import BiomassType, Pathway, Village
from services.geo import haversine_distance, estimate_trip_time_minutes
from services.engine import evaluate_eligibility, calculate_data_confidence

client = TestClient(app)


# 1. Weights Sum Test
def test_weights_sum_to_one():
    response = client.get("/api/weights")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    total = sum(item["value"] for item in data)
    assert abs(total - 1.0) < 0.001


def test_weights_update_validation():
    bad_payload = {
        "weights": {
            "w1_material_fit": 0.50,
            "w2_processing_fit": 0.20,
            "w3_logistics": 0.20,
            "w4_market_fit": 0.20,
            "w5_ease": 0.20
        }
    }
    res = client.put("/api/weights", json=bad_payload)
    assert res.status_code == 422


# 2. Haversine & Trip Time Tests
def test_haversine_and_trip_time():
    # Talaja (21.354, 72.043) to Mahuva (21.091, 71.762) is ~40-45 km
    dist = haversine_distance(21.354, 72.043, 21.091, 71.762)
    assert 38.0 < dist < 46.0

    time_mins = estimate_trip_time_minutes(dist)
    # At ~32 km/h with 1.25 circuity, ~42 km is around 90-110 minutes
    assert 75 <= time_mins <= 130


# 3. Eligibility Filter Unit Test
def test_eligibility_filter():
    db = SessionLocal()
    try:
        biomass = db.query(BiomassType).filter(BiomassType.id == "groundnut_shell").first()
        briquette_path = db.query(Pathway).filter(Pathway.id == "briquetting").first()

        # Valid input
        eligible, reasons, requires_drying = evaluate_eligibility(
            biomass=biomass,
            pathway=briquette_path,
            quantity=100.0,
            moisture_content=11.0
        )
        assert eligible is True
        assert len(reasons) == 0
        assert requires_drying is False

        # Extreme moisture (>39% for briquetting max 14%) -> ineligible
        eligible, reasons, requires_drying = evaluate_eligibility(
            biomass=biomass,
            pathway=briquette_path,
            quantity=100.0,
            moisture_content=52.0
        )
        assert eligible is False
        assert any("far exceeds maximum pathway tolerance" in r for r in reasons)
    finally:
        db.close()


# 4. Confidence Derivation Unit Test
def test_confidence_calculation():
    db = SessionLocal()
    try:
        biomass = db.query(BiomassType).filter(BiomassType.id == "groundnut_shell").first()
        pathway = db.query(Pathway).filter(Pathway.id == "briquetting").first()

        conf_high, missing_high = calculate_data_confidence(
            biomass=biomass,
            pathway=pathway,
            moisture_provided=True,
            seasonality_provided=True,
            nearest_offtaker_distance=15.0
        )
        assert conf_high in ["High", "Moderate"]
        assert not any("moisture" in m.lower() for m in missing_high)
    finally:
        db.close()


# 5. SCENARIO 1: Groundnut shells / Talaja (Bhavnagar) / 120 t/mo / 11% moisture
def test_scenario_1_talaja_groundnut_shells():
    payload = {
        "biomass_type": "groundnut_shell",
        "district_id": "bhavnagar",
        "village_id": "talaja",
        "quantity": 120.0,
        "moisture_content": 11.0,
        "seasonality_notes": "Post-Kharif harvest shells available November to February.",
        "max_radius_km": 100.0
    }
    res = client.post("/api/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["eligible_count"] > 0
    top_pathway = data["ranked_pathways"][0]
    assert top_pathway["eligible"] is True
    # Briquetting should rank top due to local Talaja briquette unit ~1-2km away
    assert top_pathway["pathway_id"] == "briquetting"
    assert top_pathway["score"] > 85.0

    # Offtakers check: must include Talaja briquette unit with very close distance
    talaja_off = next((o for o in data["nearby_offtakers"] if o["id"] == "demo_off_talaja"), None)
    assert talaja_off is not None
    assert talaja_off["distance_km"] < 5.0
    assert talaja_off["est_trip_time_mins"] is not None

    # Check nearby farmer groups and hubs
    assert len(data["nearby_farmer_groups"]) > 0
    assert len(data["nearby_hubs"]) > 0


# 6. SCENARIO 2: Cotton stalks / Limbdi / high moisture (48%)
def test_scenario_2_cotton_stalks_limbdi_high_moisture():
    payload = {
        "biomass_type": "cotton_stalk",
        "district_id": "surendranagar",
        "village_id": "limbdi",
        "quantity": 150.0,
        "moisture_content": 48.0,
        "seasonality_notes": "Fresh uprooted stalks.",
        "max_radius_km": 100.0
    }
    res = client.post("/api/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()

    # Briquetting & pelleting tolerance exceeded by >25% -> Ineligible
    briquette = next(p for p in data["ranked_pathways"] if p["pathway_id"] == "briquetting")
    pellet = next(p for p in data["ranked_pathways"] if p["pathway_id"] == "pellet_production")
    assert briquette["eligible"] is False
    assert pellet["eligible"] is False

    # Composting allows up to 55% -> Eligible
    compost = next(p for p in data["ranked_pathways"] if p["pathway_id"] == "composting")
    assert compost["eligible"] is True


# 7. SCENARIO 3: Very small quantity (5 t/month)
def test_scenario_3_small_quantity():
    payload = {
        "biomass_type": "groundnut_shell",
        "district_id": "rajkot",
        "village_id": "gondal",
        "quantity": 5.0,  # Below minimum operating scale
        "moisture_content": 10.0,
        "max_radius_km": 100.0
    }
    res = client.post("/api/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["eligible_count"] == 0
    for p in data["ranked_pathways"]:
        assert p["eligible"] is False
        assert any("minimum viable operating scale" in r for r in p["ineligibility_reasons"])


# 8. SCENARIO 4: Input with missing moisture
def test_scenario_4_missing_moisture():
    payload = {
        "biomass_type": "groundnut_shell",
        "district_id": "amreli",
        "village_id": "savarkundla",
        "quantity": 80.0,
        "moisture_content": None,
        "max_radius_km": 100.0
    }
    res = client.post("/api/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert any("moisture" in m.lower() for m in data["missing_info"])
    for p in data["ranked_pathways"]:
        if p["eligible"]:
            proc_factor = next(f for f in p["factors"] if f["factor_name"] == "Processing Requirements")
            assert proc_factor["status"] == "Requires verification"


# 9. SCENARIO 5: Village with no off-takers inside narrow radius (helpful empty state, no crash)
def test_scenario_5_no_offtakers_in_narrow_radius():
    payload = {
        "biomass_type": "cotton_stalk",
        "district_id": "kutch",
        "village_id": "anjar",
        "quantity": 60.0,
        "moisture_content": 14.0,
        "max_radius_km": 10.0  # Ultra-tight radius where no composting or biochar off-taker is present
    }
    res = client.post("/api/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()

    # Anjar only has a pellet unit demo in our dataset (accepts cotton_stalk)
    # Check that it returns cleanly, gracefully lists 0 or 1 offtaker without crashing
    assert "ranked_pathways" in data
    assert isinstance(data["nearby_offtakers"], list)
    assert isinstance(data["nearby_hubs"], list)
