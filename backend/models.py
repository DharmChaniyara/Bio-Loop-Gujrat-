"""
SQLAlchemy declarative models for BioLoop Gujarat.
Village-level granularity across Gujarat's agricultural clusters.
Every table includes source, limitations, and record_status.
"""
from sqlalchemy import Column, String, Float, Text, ForeignKey
from db import Base


class District(Base):
    __tablename__ = "districts"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False, unique=True, index=True)
    region = Column(String(64), nullable=False)  # Saurashtra, Central Gujarat, North Gujarat, South Gujarat, Kutch
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)


class Village(Base):
    __tablename__ = "villages"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False, index=True)
    taluka = Column(String(128), nullable=False, index=True)
    district_id = Column(String(64), ForeignKey("districts.id"), nullable=False, index=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    coord_precision = Column(String(32), nullable=False, default="approximate")
    primary_crops_json = Column(Text, nullable=False)  # JSON array string: ["groundnut", "cotton"]
    source = Column(String(255), nullable=False)
    limitations = Column(Text, nullable=False)
    record_status = Column(String(32), nullable=False, default="demo")


class BiomassType(Base):
    __tablename__ = "biomass_types"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    category = Column(String(64), nullable=False)
    typical_moisture_min = Column(Float, nullable=False)
    typical_moisture_max = Column(Float, nullable=False)
    harvest_months_json = Column(Text, nullable=False)  # JSON array string: ["Oct", "Nov", "Dec"]
    properties_json = Column(Text, nullable=True)       # JSON object string: calorific value, bulk density, etc.
    source = Column(String(255), nullable=False)
    limitations = Column(Text, nullable=False)
    record_status = Column(String(32), nullable=False, default="demo")


class Pathway(Base):
    __tablename__ = "pathways"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    compatible_biomass_ids = Column(Text, nullable=False)  # JSON array string: ["groundnut_shell", ...]
    max_moisture = Column(Float, nullable=False)
    min_quantity_tpm = Column(Float, nullable=False)  # minimum quantity in tonnes per month
    processing_requirements = Column(Text, nullable=False)
    capex_level = Column(String(32), nullable=False)  # 'Low' | 'Medium' | 'High'
    ease_level = Column(String(32), nullable=False)   # 'Easy' | 'Moderate' | 'Complex'
    source = Column(String(255), nullable=False)
    limitations = Column(Text, nullable=False)
    record_status = Column(String(32), nullable=False, default="demo")


class Offtaker(Base):
    __tablename__ = "offtakers"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    type = Column(String(64), nullable=False)  # 'processor' | 'aggregator' | 'composting' | 'agro-processor'
    village_id = Column(String(64), ForeignKey("villages.id"), nullable=False, index=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    accepts_biomass_ids = Column(Text, nullable=False)  # JSON array string
    pathway_ids = Column(Text, nullable=False)          # JSON array string
    capacity_tpm = Column(Float, nullable=False)        # operational capacity in tonnes/month
    listing_status = Column(String(32), nullable=False, default="demo")  # 'verified' | 'demo'
    source = Column(String(255), nullable=False)
    limitations = Column(Text, nullable=False)
    record_status = Column(String(32), nullable=False, default="demo")


class LogisticsHub(Base):
    __tablename__ = "logistics_hubs"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    village_id = Column(String(64), ForeignKey("villages.id"), nullable=False, index=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    hub_type = Column(String(64), nullable=False)  # 'collection point' | 'storage' | 'weighbridge'
    listing_status = Column(String(32), nullable=False, default="demo")
    source = Column(String(255), nullable=False)
    limitations = Column(Text, nullable=False)
    record_status = Column(String(32), nullable=False, default="demo")


class FarmerGroup(Base):
    __tablename__ = "farmer_groups"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    village_id = Column(String(64), ForeignKey("villages.id"), nullable=False, index=True)
    biomass_ids = Column(Text, nullable=False)  # JSON array string
    est_supply_tpm = Column(Float, nullable=False)
    season_months_json = Column(Text, nullable=False)  # JSON array string
    source = Column(String(255), nullable=False)
    limitations = Column(Text, nullable=False)
    record_status = Column(String(32), nullable=False, default="demo")


class Weight(Base):
    __tablename__ = "weights"

    key = Column(String(64), primary_key=True, index=True)
    value = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    source = Column(String(255), nullable=False)
    limitations = Column(Text, nullable=False)
    record_status = Column(String(32), nullable=False, default="demo")
