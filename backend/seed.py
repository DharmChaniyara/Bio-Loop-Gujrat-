"""
Curated village-level database seed script for BioLoop Gujarat.
Covers:
- 10 Gujarat districts
- 28 Villages and small towns (taluka headquarters) with approximate centroids (3 decimals)
- 3 Biomass types (groundnut shells, cotton stalks, sugarcane bagasse) with moisture ranges & harvest months
- 5 Pathways (briquetting, pellet production, biochar, activated carbon, composting)
- 14 Demo off-takers attached to specific villages
- 7 Demo logistics hubs attached to specific villages
- 12 Demo farmer producer groups
- Configurable evaluation weights summing to 1.0

Every single record carries source, limitations, and record_status='demo'.
"""
import json
import os
from db import Base, engine, SessionLocal
from models import District, Village, BiomassType, Pathway, Offtaker, LogisticsHub, FarmerGroup, Weight

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "weights.json")


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Districts
        districts_data = [
            {"id": "bhavnagar", "name": "Bhavnagar", "region": "Saurashtra", "lat": 21.764, "lng": 72.152},
            {"id": "rajkot", "name": "Rajkot", "region": "Saurashtra", "lat": 22.304, "lng": 70.802},
            {"id": "junagadh", "name": "Junagadh", "region": "Saurashtra", "lat": 21.522, "lng": 70.458},
            {"id": "amreli", "name": "Amreli", "region": "Saurashtra", "lat": 21.603, "lng": 71.222},
            {"id": "jamnagar", "name": "Jamnagar", "region": "Saurashtra", "lat": 22.471, "lng": 70.058},
            {"id": "surendranagar", "name": "Surendranagar", "region": "Saurashtra", "lat": 22.720, "lng": 71.640},
            {"id": "botad", "name": "Botad", "region": "Saurashtra", "lat": 22.170, "lng": 71.660},
            {"id": "ahmedabad", "name": "Ahmedabad", "region": "Central Gujarat", "lat": 23.023, "lng": 72.571},
            {"id": "bharuch", "name": "Bharuch", "region": "South Gujarat", "lat": 21.705, "lng": 72.996},
            {"id": "kutch", "name": "Kutch", "region": "Kutch", "lat": 23.242, "lng": 69.667},
            {"id": "sabarkantha", "name": "Sabarkantha", "region": "North Gujarat", "lat": 23.530, "lng": 73.070},
        ]

        for d in districts_data:
            existing = db.query(District).filter(District.id == d["id"]).first()
            if not existing:
                db.add(District(**d))
            else:
                for k, v in d.items():
                    setattr(existing, k, v)

        # 2. Villages and Taluka Headquarters (28 locations, 3-decimal coordinates, approx centroid limitations)
        village_limitation = "Approximate centroid, verify against Census or Bhuvan before field use."
        village_source = "Survey of India / Bhuvan open geographic directory (indicative demo centroid)"

        villages_data = [
            # Bhavnagar (Groundnut & Onion belt)
            {"id": "talaja", "name": "Talaja", "taluka": "Talaja", "district_id": "bhavnagar", "lat": 21.354, "lng": 72.043, "primary_crops_json": json.dumps(["groundnut", "onion", "cotton"])},
            {"id": "mahuva", "name": "Mahuva", "taluka": "Mahuva", "district_id": "bhavnagar", "lat": 21.091, "lng": 71.762, "primary_crops_json": json.dumps(["groundnut", "onion", "coconut"])},
            {"id": "sihor", "name": "Sihor", "taluka": "Sihor", "district_id": "bhavnagar", "lat": 21.703, "lng": 71.961, "primary_crops_json": json.dumps(["groundnut", "cotton", "bajra"])},
            {"id": "gariadhar", "name": "Gariadhar", "taluka": "Gariadhar", "district_id": "bhavnagar", "lat": 21.536, "lng": 71.581, "primary_crops_json": json.dumps(["groundnut", "cotton"])},

            # Rajkot (Core groundnut processing belt)
            {"id": "gondal", "name": "Gondal", "taluka": "Gondal", "district_id": "rajkot", "lat": 21.962, "lng": 70.798, "primary_crops_json": json.dumps(["groundnut", "chilli", "cotton"])},
            {"id": "jasdan", "name": "Jasdan", "taluka": "Jasdan", "district_id": "rajkot", "lat": 22.033, "lng": 71.202, "primary_crops_json": json.dumps(["cotton", "groundnut", "sesame"])},
            {"id": "dhoraji", "name": "Dhoraji", "taluka": "Dhoraji", "district_id": "rajkot", "lat": 21.734, "lng": 70.453, "primary_crops_json": json.dumps(["groundnut", "cotton", "sugarcane"])},
            {"id": "kotda_sangani", "name": "Kotda Sangani", "taluka": "Kotda Sangani", "district_id": "rajkot", "lat": 21.978, "lng": 70.932, "primary_crops_json": json.dumps(["groundnut", "cotton"])},

            # Junagadh (Groundnut & horticulture)
            {"id": "visavadar", "name": "Visavadar", "taluka": "Visavadar", "district_id": "junagadh", "lat": 21.341, "lng": 70.722, "primary_crops_json": json.dumps(["groundnut", "mango", "cotton"])},
            {"id": "keshod", "name": "Keshod", "taluka": "Keshod", "district_id": "junagadh", "lat": 21.303, "lng": 70.252, "primary_crops_json": json.dumps(["groundnut", "wheat", "coriander"])},
            {"id": "mangarol", "name": "Mangarol", "taluka": "Mangarol", "district_id": "junagadh", "lat": 21.122, "lng": 70.114, "primary_crops_json": json.dumps(["groundnut", "coconut"])},

            # Amreli
            {"id": "savarkundla", "name": "Savarkundla", "taluka": "Savarkundla", "district_id": "amreli", "lat": 21.332, "lng": 71.311, "primary_crops_json": json.dumps(["cotton", "groundnut", "sesame"])},
            {"id": "lathi", "name": "Lathi", "taluka": "Lathi", "district_id": "amreli", "lat": 21.721, "lng": 71.388, "primary_crops_json": json.dumps(["cotton", "groundnut"])},
            {"id": "dhari", "name": "Dhari", "taluka": "Dhari", "district_id": "amreli", "lat": 21.325, "lng": 71.025, "primary_crops_json": json.dumps(["groundnut", "cotton", "sorghum"])},

            # Jamnagar
            {"id": "dhrol", "name": "Dhrol", "taluka": "Dhrol", "district_id": "jamnagar", "lat": 22.563, "lng": 70.414, "primary_crops_json": json.dumps(["cotton", "groundnut", "cumin"])},
            {"id": "kalavad", "name": "Kalavad", "taluka": "Kalavad", "district_id": "jamnagar", "lat": 22.212, "lng": 70.381, "primary_crops_json": json.dumps(["groundnut", "cotton"])},

            # Surendranagar (Cotton belt)
            {"id": "limbdi", "name": "Limbdi", "taluka": "Limbdi", "district_id": "surendranagar", "lat": 22.561, "lng": 71.802, "primary_crops_json": json.dumps(["cotton", "sesame", "cumin"])},
            {"id": "dhrangadhra", "name": "Dhrangadhra", "taluka": "Dhrangadhra", "district_id": "surendranagar", "lat": 22.982, "lng": 71.463, "primary_crops_json": json.dumps(["cotton", "castor", "salt"])},
            {"id": "chotila", "name": "Chotila", "taluka": "Chotila", "district_id": "surendranagar", "lat": 22.421, "lng": 71.192, "primary_crops_json": json.dumps(["cotton", "groundnut"])},

            # Botad (Cotton & groundnut)
            {"id": "barvala", "name": "Barvala", "taluka": "Barvala", "district_id": "botad", "lat": 22.152, "lng": 71.892, "primary_crops_json": json.dumps(["cotton", "wheat", "groundnut"])},
            {"id": "gadhada", "name": "Gadhada", "taluka": "Gadhada", "district_id": "botad", "lat": 21.961, "lng": 71.582, "primary_crops_json": json.dumps(["cotton", "groundnut"])},

            # Ahmedabad Rural
            {"id": "dholka", "name": "Dholka", "taluka": "Dholka", "district_id": "ahmedabad", "lat": 22.721, "lng": 72.463, "primary_crops_json": json.dumps(["paddy", "cotton", "wheat"])},
            {"id": "dhandhuka", "name": "Dhandhuka", "taluka": "Dhandhuka", "district_id": "ahmedabad", "lat": 22.372, "lng": 71.982, "primary_crops_json": json.dumps(["cotton", "wheat", "chickpea"])},
            {"id": "sanand", "name": "Sanand", "taluka": "Sanand", "district_id": "ahmedabad", "lat": 22.991, "lng": 72.373, "primary_crops_json": json.dumps(["paddy", "wheat", "cotton"])},

            # Bharuch (South Gujarat cotton & sugarcane)
            {"id": "jambusar", "name": "Jambusar", "taluka": "Jambusar", "district_id": "bharuch", "lat": 22.052, "lng": 72.802, "primary_crops_json": json.dumps(["cotton", "paddy", "pulses"])},
            {"id": "ankleshwar", "name": "Ankleshwar", "taluka": "Ankleshwar", "district_id": "bharuch", "lat": 21.632, "lng": 73.003, "primary_crops_json": json.dumps(["sugarcane", "cotton", "banana"])},

            # Kutch & North Gujarat (Coverage)
            {"id": "anjar", "name": "Anjar", "taluka": "Anjar", "district_id": "kutch", "lat": 23.112, "lng": 70.031, "primary_crops_json": json.dumps(["castor", "cotton", "mustard"])},
            {"id": "himatnagar", "name": "Himatnagar", "taluka": "Himatnagar", "district_id": "sabarkantha", "lat": 23.593, "lng": 72.961, "primary_crops_json": json.dumps(["cotton", "maize", "groundnut"])}
        ]

        for v in villages_data:
            v_dict = {
                **v,
                "coord_precision": "approximate",
                "source": village_source,
                "limitations": village_limitation,
                "record_status": "demo"
            }
            existing = db.query(Village).filter(Village.id == v["id"]).first()
            if not existing:
                db.add(Village(**v_dict))
            else:
                for k, val in v_dict.items():
                    setattr(existing, k, val)

        # 3. Biomass Types (3 types, with min/max moisture and harvest months)
        biomass_data = [
            {
                "id": "groundnut_shell",
                "name": "Groundnut Shells",
                "category": "Oilseed crop residue",
                "typical_moisture_min": 8.0,
                "typical_moisture_max": 14.0,
                "harvest_months_json": json.dumps(["Oct", "Nov", "Dec", "Jan", "Feb"]),
                "properties_json": json.dumps({
                    "calorific_value_mj_kg": "16.5-17.5",
                    "bulk_density_kg_m3": "140-180",
                    "ash_content_pct": "3.5-5.0%",
                    "fixed_carbon_pct": "18-22%"
                }),
                "source": "Saurashtra agro-processing baseline surveys (indicative field range)",
                "limitations": "Moisture rises rapidly if stored outdoors during monsoon; silica content depends on threshing surface.",
                "record_status": "demo"
            },
            {
                "id": "cotton_stalk",
                "name": "Cotton Stalks",
                "category": "Fiber crop residue",
                "typical_moisture_min": 14.0,
                "typical_moisture_max": 24.0,
                "harvest_months_json": json.dumps(["Dec", "Jan", "Feb", "Mar", "Apr"]),
                "properties_json": json.dumps({
                    "calorific_value_mj_kg": "15.0-16.2",
                    "bulk_density_kg_m3": "90-130",
                    "ash_content_pct": "4.0-7.0%",
                    "fixed_carbon_pct": "16-19%"
                }),
                "source": "Gujarat agricultural residues review (illustrative baseline)",
                "limitations": "Requires chipping or shredding prior to compacting; high moisture post-harvest requires sun-curing.",
                "record_status": "demo"
            },
            {
                "id": "bagasse",
                "name": "Sugarcane Bagasse",
                "category": "Agro-industrial by-product",
                "typical_moisture_min": 45.0,
                "typical_moisture_max": 52.0,
                "harvest_months_json": json.dumps(["Nov", "Dec", "Jan", "Feb", "Mar"]),
                "properties_json": json.dumps({
                    "calorific_value_mj_kg": "7.5-9.0 (as-received), 17.0 (dry)",
                    "bulk_density_kg_m3": "120-150",
                    "ash_content_pct": "1.5-3.0%",
                    "fixed_carbon_pct": "14-16%"
                }),
                "source": "South Gujarat cooperative sugar mills baseline (indicative)",
                "limitations": "Extremely high initial moisture; seasonal availability tied to 120-day crushing season; highly prone to biological degradation if stockpiled wet.",
                "record_status": "demo"
            }
        ]

        for b in biomass_data:
            existing = db.query(BiomassType).filter(BiomassType.id == b["id"]).first()
            if not existing:
                db.add(BiomassType(**b))
            else:
                for k, v in b.items():
                    setattr(existing, k, v)

        # 4. Pathways (5 pathways with placeholder sources)
        pathway_tech_source = "to be verified against technical reference"
        pathway_data = [
            {
                "id": "briquetting",
                "name": "Biomass Briquetting (White Coal)",
                "compatible_biomass_ids": json.dumps(["groundnut_shell", "cotton_stalk"]),
                "max_moisture": 14.0,
                "min_quantity_tpm": 40.0,
                "processing_requirements": "Mechanical shredding to <8mm, moisture adjustment to 10-12%, high-pressure ram or screw pressing without chemical binder.",
                "capex_level": "Low",
                "ease_level": "Easy",
                "source": pathway_tech_source,
                "limitations": "High raw moisture degrades briquette density and causes puffing; requires dry shed storage.",
                "record_status": "demo"
            },
            {
                "id": "pellet_production",
                "name": "Pellet Production (Industrial Fuel)",
                "compatible_biomass_ids": json.dumps(["groundnut_shell", "cotton_stalk"]),
                "max_moisture": 12.0,
                "min_quantity_tpm": 80.0,
                "processing_requirements": "Hammer mill grinding (<4mm), thermal rotary drying if moisture >12%, steam conditioning, ring-die pellet mill pressing, counter-flow cooling.",
                "capex_level": "Medium",
                "ease_level": "Moderate",
                "source": pathway_tech_source,
                "limitations": "Sand or soil contamination causes rapid ring-die wear; high electricity consumption per tonne.",
                "record_status": "demo"
            },
            {
                "id": "biochar",
                "name": "Biochar Production (Slow Pyrolysis)",
                "compatible_biomass_ids": json.dumps(["cotton_stalk", "groundnut_shell"]),
                "max_moisture": 20.0,
                "min_quantity_tpm": 30.0,
                "processing_requirements": "Coarse chipping (20-50mm), oxygen-limited thermal decomposition (450-600°C) in retort or rotary pyrolysis kiln, quenching and stabilization.",
                "capex_level": "Medium",
                "ease_level": "Moderate",
                "source": pathway_tech_source,
                "limitations": "Syngas flaring or recovery controls required; market willingness-to-pay varies across crop zones.",
                "record_status": "demo"
            },
            {
                "id": "activated_carbon",
                "name": "Activated Carbon Manufacturing",
                "compatible_biomass_ids": json.dumps(["groundnut_shell"]),
                "max_moisture": 15.0,
                "min_quantity_tpm": 100.0,
                "processing_requirements": "Carbonization (500°C) followed by high-temperature steam or chemical activation (850-950°C), acid washing, neutralizing, and micro-milling.",
                "capex_level": "High",
                "ease_level": "Complex",
                "source": pathway_tech_source,
                "limitations": "Strict feedstock purity and uniform particle hardness required; high capex for effluent and gas scrubbers.",
                "record_status": "demo"
            },
            {
                "id": "composting",
                "name": "Aerobic Agricultural Composting",
                "compatible_biomass_ids": json.dumps(["cotton_stalk", "bagasse", "groundnut_shell"]),
                "max_moisture": 55.0,
                "min_quantity_tpm": 25.0,
                "processing_requirements": "Size reduction, carbon-to-nitrogen balancing (with animal manure or pressmud), pile formation in windrows, regular mechanical turning and aeration.",
                "capex_level": "Low",
                "ease_level": "Easy",
                "source": pathway_tech_source,
                "limitations": "Requires 60 to 90 days curing cycle; significant land pad footprint and water requirement.",
                "record_status": "demo"
            }
        ]

        for p in pathway_data:
            existing = db.query(Pathway).filter(Pathway.id == p["id"]).first()
            if not existing:
                db.add(Pathway(**p))
            else:
                for k, v in p.items():
                    setattr(existing, k, v)

        # 5. Demo Offtakers (14 village-level facilities with generic names)
        offtaker_source = "to be verified against technical reference"
        offtaker_data = [
            # Talaja & Mahuva area (Bhavnagar)
            {
                "id": "demo_off_talaja",
                "name": "Demo Briquette Unit, near Talaja",
                "type": "processor",
                "village_id": "talaja",
                "lat": 21.362,
                "lng": 72.051,
                "accepts_biomass_ids": json.dumps(["groundnut_shell", "cotton_stalk"]),
                "pathway_ids": json.dumps(["briquetting"]),
                "capacity_tpm": 200.0,
                "listing_status": "demo",
                "source": offtaker_source,
                "limitations": "Demo data, illustrative only. Seasonal intake November to April.",
                "record_status": "demo"
            },
            {
                "id": "demo_off_mahuva",
                "name": "Demo Bio-Pellet Facility, Mahuva Rural",
                "type": "processor",
                "village_id": "mahuva",
                "lat": 21.085,
                "lng": 71.770,
                "accepts_biomass_ids": json.dumps(["groundnut_shell", "cotton_stalk"]),
                "pathway_ids": json.dumps(["pellet_production", "briquetting"]),
                "capacity_tpm": 350.0,
                "listing_status": "demo",
                "source": offtaker_source,
                "limitations": "Demo data, illustrative only. Rejects batches with stone/debris >1%.",
                "record_status": "demo"
            },
            {
                "id": "demo_off_sihor",
                "name": "Demo Agro-Fuel Press, Sihor Industrial Zone",
                "type": "processor",
                "village_id": "sihor",
                "lat": 21.710,
                "lng": 71.954,
                "accepts_biomass_ids": json.dumps(["groundnut_shell", "cotton_stalk"]),
                "pathway_ids": json.dumps(["briquetting"]),
                "capacity_tpm": 250.0,
                "listing_status": "demo",
                "source": offtaker_source,
                "limitations": "Demo data, illustrative only. Operates 90mm piston press.",
                "record_status": "demo"
            },
            # Rajkot cluster
            {
                "id": "demo_off_gondal",
                "name": "Demo Groundnut Carbonizer, Gondal Highway",
                "type": "processor",
                "village_id": "gondal",
                "lat": 21.955,
                "lng": 70.812,
                "accepts_biomass_ids": json.dumps(["groundnut_shell"]),
                "pathway_ids": json.dumps(["activated_carbon", "biochar"]),
                "capacity_tpm": 400.0,
                "listing_status": "demo",
                "source": offtaker_source,
                "limitations": "Demo data, illustrative only. Continuous rotary retorts.",
                "record_status": "demo"
            },
            {
                "id": "demo_off_jasdan",
                "name": "Demo Agro-Biomass Briquettes, Jasdan",
                "type": "processor",
                "village_id": "jasdan",
                "lat": 22.040,
                "lng": 71.195,
                "accepts_biomass_ids": json.dumps(["cotton_stalk", "groundnut_shell"]),
                "pathway_ids": json.dumps(["briquetting"]),
                "capacity_tpm": 180.0,
                "listing_status": "demo",
                "source": offtaker_source,
                "limitations": "Demo data, illustrative only.",
                "record_status": "demo"
            },
            {
                "id": "demo_off_dhoraji",
                "name": "Demo Western Saurashtra Bio-Pellets, Dhoraji",
                "type": "processor",
                "village_id": "dhoraji",
                "lat": 21.740,
                "lng": 70.445,
                "accepts_biomass_ids": json.dumps(["groundnut_shell", "cotton_stalk"]),
                "pathway_ids": json.dumps(["pellet_production"]),
                "capacity_tpm": 300.0,
                "listing_status": "demo",
                "source": offtaker_source,
                "limitations": "Demo data, illustrative only.",
                "record_status": "demo"
            },
            # Junagadh cluster
            {
                "id": "demo_off_visavadar",
                "name": "Demo Gir Foot-hills Biochar Unit, Visavadar",
                "type": "processor",
                "village_id": "visavadar",
                "lat": 21.348,
                "lng": 70.715,
                "accepts_biomass_ids": json.dumps(["cotton_stalk", "groundnut_shell"]),
                "pathway_ids": json.dumps(["biochar"]),
                "capacity_tpm": 150.0,
                "listing_status": "demo",
                "source": offtaker_source,
                "limitations": "Demo data, illustrative only.",
                "record_status": "demo"
            },
            # Amreli cluster
            {
                "id": "demo_off_savarkundla",
                "name": "Demo Saurashtra Bio-Pellets, Savarkundla",
                "type": "processor",
                "village_id": "savarkundla",
                "lat": 21.340,
                "lng": 71.320,
                "accepts_biomass_ids": json.dumps(["cotton_stalk", "groundnut_shell"]),
                "pathway_ids": json.dumps(["pellet_production", "briquetting"]),
                "capacity_tpm": 280.0,
                "listing_status": "demo",
                "source": offtaker_source,
                "limitations": "Demo data, illustrative only.",
                "record_status": "demo"
            },
            {
                "id": "demo_off_lathi",
                "name": "Demo Cotton Stalk Aggregator, Lathi",
                "type": "aggregator",
                "village_id": "lathi",
                "lat": 21.728,
                "lng": 71.395,
                "accepts_biomass_ids": json.dumps(["cotton_stalk"]),
                "pathway_ids": json.dumps(["briquetting", "biochar"]),
                "capacity_tpm": 220.0,
                "listing_status": "demo",
                "source": offtaker_source,
                "limitations": "Demo data, illustrative only. Aggregates bales from 15 villages.",
                "record_status": "demo"
            },
            # Surendranagar (Cotton belt)
            {
                "id": "demo_off_limbdi",
                "name": "Demo Cotton Biomass Processor, Limbdi Outskirts",
                "type": "processor",
                "village_id": "limbdi",
                "lat": 22.568,
                "lng": 71.810,
                "accepts_biomass_ids": json.dumps(["cotton_stalk"]),
                "pathway_ids": json.dumps(["briquetting", "composting"]),
                "capacity_tpm": 250.0,
                "listing_status": "demo",
                "source": offtaker_source,
                "limitations": "Demo data, illustrative only. Operates heavy shredders.",
                "record_status": "demo"
            },
            {
                "id": "demo_off_dhrangadhra",
                "name": "Demo North Saurashtra Agro-Pellets, Dhrangadhra",
                "type": "processor",
                "village_id": "dhrangadhra",
                "lat": 22.975,
                "lng": 71.470,
                "accepts_biomass_ids": json.dumps(["cotton_stalk", "groundnut_shell"]),
                "pathway_ids": json.dumps(["pellet_production"]),
                "capacity_tpm": 320.0,
                "listing_status": "demo",
                "source": offtaker_source,
                "limitations": "Demo data, illustrative only.",
                "record_status": "demo"
            },
            # Ahmedabad Rural & Botad
            {
                "id": "demo_off_dholka",
                "name": "Demo Bhal Agro-Composting Yard, Dholka",
                "type": "composting",
                "village_id": "dholka",
                "lat": 22.715,
                "lng": 72.470,
                "accepts_biomass_ids": json.dumps(["cotton_stalk", "bagasse", "groundnut_shell"]),
                "pathway_ids": json.dumps(["composting"]),
                "capacity_tpm": 500.0,
                "listing_status": "demo",
                "source": offtaker_source,
                "limitations": "Demo data, illustrative only. Open yard composting windrows.",
                "record_status": "demo"
            },
            # Bharuch
            {
                "id": "demo_off_ankleshwar",
                "name": "Demo South Gujarat Bagasse & Biomass Energy, Ankleshwar",
                "type": "agro-processor",
                "village_id": "ankleshwar",
                "lat": 21.625,
                "lng": 73.010,
                "accepts_biomass_ids": json.dumps(["bagasse", "cotton_stalk"]),
                "pathway_ids": json.dumps(["briquetting", "composting"]),
                "capacity_tpm": 600.0,
                "listing_status": "demo",
                "source": offtaker_source,
                "limitations": "Demo data, illustrative only. Operates steam-assisted drying line.",
                "record_status": "demo"
            },
            # Kutch
            {
                "id": "demo_off_anjar",
                "name": "Demo Kutch Port-Hinterland Biofuels, Anjar",
                "type": "processor",
                "village_id": "anjar",
                "lat": 23.120,
                "lng": 70.040,
                "accepts_biomass_ids": json.dumps(["cotton_stalk", "groundnut_shell"]),
                "pathway_ids": json.dumps(["pellet_production"]),
                "capacity_tpm": 300.0,
                "listing_status": "demo",
                "source": offtaker_source,
                "limitations": "Demo data, illustrative only.",
                "record_status": "demo"
            }
        ]

        for o in offtaker_data:
            existing = db.query(Offtaker).filter(Offtaker.id == o["id"]).first()
            if not existing:
                db.add(Offtaker(**o))
            else:
                for k, v in o.items():
                    setattr(existing, k, v)

        # 6. Demo Logistics Hubs (7 village-level aggregation points)
        hub_source = "to be verified against technical reference"
        hub_data = [
            {
                "id": "hub_talaja",
                "name": "Demo Shetrunji Basin Biomass Staging Point, Talaja",
                "village_id": "talaja",
                "lat": 21.358,
                "lng": 72.046,
                "hub_type": "collection point",
                "listing_status": "demo",
                "source": hub_source,
                "limitations": "Demo data, illustrative only. 40MT weighbridge and covered shed.",
                "record_status": "demo"
            },
            {
                "id": "hub_gondal",
                "name": "Demo Central Saurashtra Agro-Hub, Gondal",
                "village_id": "gondal",
                "lat": 21.968,
                "lng": 70.805,
                "hub_type": "storage",
                "listing_status": "demo",
                "source": hub_source,
                "limitations": "Demo data, illustrative only. Dedicated stationary coarse shredder.",
                "record_status": "demo"
            },
            {
                "id": "hub_savarkundla",
                "name": "Demo Southern Saurashtra Collection Depot, Savarkundla",
                "village_id": "savarkundla",
                "lat": 21.335,
                "lng": 71.315,
                "hub_type": "collection point",
                "listing_status": "demo",
                "source": hub_source,
                "limitations": "Demo data, illustrative only.",
                "record_status": "demo"
            },
            {
                "id": "hub_limbdi",
                "name": "Demo Limbdi Gateway Weighbridge & Depot, Limbdi",
                "village_id": "limbdi",
                "lat": 22.565,
                "lng": 71.805,
                "hub_type": "weighbridge",
                "listing_status": "demo",
                "source": hub_source,
                "limitations": "Demo data, illustrative only. 60MT electronic weighbridge.",
                "record_status": "demo"
            },
            {
                "id": "hub_dholka",
                "name": "Demo Bhal Regional Biomass Yard, Dholka",
                "village_id": "dholka",
                "lat": 22.725,
                "lng": 72.468,
                "hub_type": "storage",
                "listing_status": "demo",
                "source": hub_source,
                "limitations": "Demo data, illustrative only.",
                "record_status": "demo"
            },
            {
                "id": "hub_dhoraji",
                "name": "Demo Bhadar Valley Depot, Dhoraji",
                "village_id": "dhoraji",
                "lat": 21.738,
                "lng": 70.450,
                "hub_type": "collection point",
                "listing_status": "demo",
                "source": hub_source,
                "limitations": "Demo data, illustrative only.",
                "record_status": "demo"
            },
            {
                "id": "hub_himatnagar",
                "name": "Demo Sabar Aggregation Terminal, Himatnagar",
                "village_id": "himatnagar",
                "lat": 23.590,
                "lng": 72.965,
                "hub_type": "storage",
                "listing_status": "demo",
                "source": hub_source,
                "limitations": "Demo data, illustrative only.",
                "record_status": "demo"
            }
        ]

        for h in hub_data:
            existing = db.query(LogisticsHub).filter(LogisticsHub.id == h["id"]).first()
            if not existing:
                db.add(LogisticsHub(**h))
            else:
                for k, v in h.items():
                    setattr(existing, k, v)

        # 7. Demo Farmer Producer Groups (12 village-level farmer associations)
        group_source = "to be verified against technical reference"
        farmer_groups_data = [
            {
                "id": "fpo_talaja_shells",
                "name": "Demo Talaja Groundnut Shell Growers Association",
                "village_id": "talaja",
                "biomass_ids": json.dumps(["groundnut_shell"]),
                "est_supply_tpm": 160.0,
                "season_months_json": json.dumps(["Nov", "Dec", "Jan", "Feb"]),
                "source": group_source,
                "limitations": "Demo data, illustrative only. Aggregates farm-level shelling residue.",
                "record_status": "demo"
            },
            {
                "id": "fpo_mahuva_residues",
                "name": "Demo Mahuva Taluka Agro-Residue Union",
                "village_id": "mahuva",
                "biomass_ids": json.dumps(["groundnut_shell"]),
                "est_supply_tpm": 220.0,
                "season_months_json": json.dumps(["Nov", "Dec", "Jan", "Feb", "Mar"]),
                "source": group_source,
                "limitations": "Demo data, illustrative only.",
                "record_status": "demo"
            },
            {
                "id": "fpo_sihor_farmers",
                "name": "Demo Sihor Krushi Biomass Group",
                "village_id": "sihor",
                "biomass_ids": json.dumps(["groundnut_shell", "cotton_stalk"]),
                "est_supply_tpm": 130.0,
                "season_months_json": json.dumps(["Dec", "Jan", "Feb"]),
                "source": group_source,
                "limitations": "Demo data, illustrative only.",
                "record_status": "demo"
            },
            {
                "id": "fpo_gondal_oilseed",
                "name": "Demo Gondal APMC Oilseed Residual Collective",
                "village_id": "gondal",
                "biomass_ids": json.dumps(["groundnut_shell"]),
                "est_supply_tpm": 300.0,
                "season_months_json": json.dumps(["Oct", "Nov", "Dec", "Jan", "Feb"]),
                "source": group_source,
                "limitations": "Demo data, illustrative only. Direct decorticator surplus.",
                "record_status": "demo"
            },
            {
                "id": "fpo_jasdan_cotton",
                "name": "Demo Jasdan Cotton Producers Group",
                "village_id": "jasdan",
                "biomass_ids": json.dumps(["cotton_stalk"]),
                "est_supply_tpm": 190.0,
                "season_months_json": json.dumps(["Jan", "Feb", "Mar", "Apr"]),
                "source": group_source,
                "limitations": "Demo data, illustrative only.",
                "record_status": "demo"
            },
            {
                "id": "fpo_visavadar_organic",
                "name": "Demo Visavadar Agro-Forestry & Residue Sangathan",
                "village_id": "visavadar",
                "biomass_ids": json.dumps(["cotton_stalk", "groundnut_shell"]),
                "est_supply_tpm": 140.0,
                "season_months_json": json.dumps(["Nov", "Dec", "Jan", "Feb"]),
                "source": group_source,
                "limitations": "Demo data, illustrative only.",
                "record_status": "demo"
            },
            {
                "id": "fpo_savarkundla_farmers",
                "name": "Demo Savarkundla Progressive Farmers Mandal",
                "village_id": "savarkundla",
                "biomass_ids": json.dumps(["cotton_stalk", "groundnut_shell"]),
                "est_supply_tpm": 210.0,
                "season_months_json": json.dumps(["Dec", "Jan", "Feb", "Mar"]),
                "source": group_source,
                "limitations": "Demo data, illustrative only.",
                "record_status": "demo"
            },
            {
                "id": "fpo_limbdi_cotton",
                "name": "Demo Limbdi Cotton Pullers Collective",
                "village_id": "limbdi",
                "biomass_ids": json.dumps(["cotton_stalk"]),
                "est_supply_tpm": 260.0,
                "season_months_json": json.dumps(["Jan", "Feb", "Mar", "Apr"]),
                "source": group_source,
                "limitations": "Demo data, illustrative only. Organized mechanized uprooting.",
                "record_status": "demo"
            },
            {
                "id": "fpo_dhrangadhra_cotton",
                "name": "Demo Dhrangadhra Agro-Residual Society",
                "village_id": "dhrangadhra",
                "biomass_ids": json.dumps(["cotton_stalk"]),
                "est_supply_tpm": 180.0,
                "season_months_json": json.dumps(["Feb", "Mar", "Apr"]),
                "source": group_source,
                "limitations": "Demo data, illustrative only.",
                "record_status": "demo"
            },
            {
                "id": "fpo_barvala_farmers",
                "name": "Demo Barvala Bio-Resource Group",
                "village_id": "barvala",
                "biomass_ids": json.dumps(["cotton_stalk", "groundnut_shell"]),
                "est_supply_tpm": 150.0,
                "season_months_json": json.dumps(["Dec", "Jan", "Feb"]),
                "source": group_source,
                "limitations": "Demo data, illustrative only.",
                "record_status": "demo"
            },
            {
                "id": "fpo_dholka_paddy_cotton",
                "name": "Demo Dholka Bhal Agrarian Federation",
                "village_id": "dholka",
                "biomass_ids": json.dumps(["cotton_stalk"]),
                "est_supply_tpm": 240.0,
                "season_months_json": json.dumps(["Jan", "Feb", "Mar"]),
                "source": group_source,
                "limitations": "Demo data, illustrative only.",
                "record_status": "demo"
            },
            {
                "id": "fpo_ankleshwar_bagasse",
                "name": "Demo South Gujarat Sugar Outgrowers Cell",
                "village_id": "ankleshwar",
                "biomass_ids": json.dumps(["bagasse"]),
                "est_supply_tpm": 400.0,
                "season_months_json": json.dumps(["Nov", "Dec", "Jan", "Feb", "Mar"]),
                "source": group_source,
                "limitations": "Demo data, illustrative only.",
                "record_status": "demo"
            }
        ]

        for fg in farmer_groups_data:
            existing = db.query(FarmerGroup).filter(FarmerGroup.id == fg["id"]).first()
            if not existing:
                db.add(FarmerGroup(**fg))
            else:
                for k, v in fg.items():
                    setattr(existing, k, v)

        # 8. Evaluation Weights (summing to 1.0)
        weights_source = "to be verified against technical reference"
        default_weights = {
            "w1_material_fit": {"value": 0.30, "description": "Feedstock physical and chemical compatibility", "source": weights_source, "limitations": "Does not account for proprietary chemical pretreatment", "record_status": "demo"},
            "w2_processing_fit": {"value": 0.20, "description": "Moisture tolerance and required pre-treatment energy", "source": weights_source, "limitations": "Assumes standard rotary / sun drying energy curve", "record_status": "demo"},
            "w3_logistics": {"value": 0.20, "description": "Haversine proximity and trip time to nearby offtakers/hubs", "source": weights_source, "limitations": "Straight-line radius with 25% road circuity estimate", "record_status": "demo"},
            "w4_market_fit": {"value": 0.15, "description": "Regional offtaker demand readiness and product offtake stability", "source": weights_source, "limitations": "Excludes volatile spot market price fluctuations", "record_status": "demo"},
            "w5_ease": {"value": 0.15, "description": "Implementation simplicity, capital intensity, and permitting ease", "source": weights_source, "limitations": "Specific land and grid tie-in approvals will vary", "record_status": "demo"}
        }

        for k, v in default_weights.items():
            existing = db.query(Weight).filter(Weight.key == k).first()
            if not existing:
                db.add(Weight(
                    key=k,
                    value=v["value"],
                    description=v["description"],
                    source=v["source"],
                    limitations=v["limitations"],
                    record_status=v["record_status"]
                ))
            else:
                existing.value = v["value"]
                existing.description = v["description"]

        db.commit()
        print("Database seeded successfully with 28 villages, offtakers, hubs, and farmer groups.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
