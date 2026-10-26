import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import BiomassInputForm from './components/BiomassInputForm';
import PathwayList from './components/PathwayList';
import FactorBreakdown from './components/FactorBreakdown';
import OfftakerMap from './components/OfftakerMap';
import CompareTable from './components/CompareTable';
import WeightsDrawer from './components/WeightsDrawer';
import {
  fetchBiomassTypes,
  fetchDistricts,
  fetchVillages,
  fetchWeights,
  updateWeights,
  evaluateBiomass
} from './api/client';
import './styles/app.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('input'); // 'input' | 'pathways' | 'explanation' | 'map' | 'compare'
  const [biomassTypes, setBiomassTypes] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [selectedDistrictId, setSelectedDistrictId] = useState('bhavnagar');
  const [villages, setVillages] = useState([]);
  const [weights, setWeights] = useState([]);
  const [isWeightsOpen, setIsWeightsOpen] = useState(false);

  // Evaluation State
  const [evalLoading, setEvalLoading] = useState(false);
  const [evalError, setEvalError] = useState(null);
  const [evaluationResult, setEvaluationResult] = useState(null);
  const [selectedPathwayId, setSelectedPathwayId] = useState(null);

  // Initial load
  useEffect(() => {
    async function loadInitialData() {
      try {
        const [bioData, distData, wData] = await Promise.all([
          fetchBiomassTypes(),
          fetchDistricts(),
          fetchWeights(),
        ]);
        setBiomassTypes(bioData);
        setDistricts(distData);
        setWeights(wData);
      } catch (err) {
        console.error('Failed to load initial metadata:', err);
      }
    }
    loadInitialData();
  }, []);

  // Fetch villages when selected district changes
  useEffect(() => {
    async function loadVillages() {
      try {
        const vData = await fetchVillages(selectedDistrictId);
        setVillages(vData);
      } catch (err) {
        console.error('Failed to load villages:', err);
      }
    }
    if (selectedDistrictId) {
      loadVillages();
    }
  }, [selectedDistrictId]);

  // Tab switching with View Transitions API where supported
  const switchTab = (tabId) => {
    if (document.startViewTransition) {
      document.startViewTransition(() => {
        setActiveTab(tabId);
      });
    } else {
      setActiveTab(tabId);
    }
  };

  // Evaluation submission
  const handleRunEvaluation = async (formData) => {
    setEvalLoading(true);
    setEvalError(null);
    try {
      const result = await evaluateBiomass(formData);
      setEvaluationResult(result);
      if (result.ranked_pathways && result.ranked_pathways.length > 0) {
        setSelectedPathwayId(result.ranked_pathways[0].pathway_id);
      }
      switchTab('pathways');
    } catch (err) {
      setEvalError(err.message || 'Evaluation failed');
    } finally {
      setEvalLoading(false);
    }
  };

  const handleSaveWeights = async (newWeightsMap) => {
    const updated = await updateWeights(newWeightsMap);
    setWeights(updated);
    if (evaluationResult && evaluationResult.input_summary) {
      const inp = evaluationResult.input_summary;
      handleRunEvaluation({
        biomass_type: inp.biomass_id,
        district_id: inp.district_id,
        village_id: inp.village_id,
        quantity: inp.quantity_tpm,
        moisture_content: inp.moisture_content_pct,
        seasonality_notes: inp.seasonality_notes,
        max_radius_km: evaluationResult.catchment_radius_km || 100.0,
      });
    }
  };

  const selectedPathway = evaluationResult?.ranked_pathways?.find(
    (p) => p.pathway_id === selectedPathwayId
  );

  const originVillage = evaluationResult?.input_summary ? {
    id: evaluationResult.input_summary.village_id,
    name: evaluationResult.input_summary.village_name,
    taluka: evaluationResult.input_summary.taluka,
    district_id: evaluationResult.input_summary.district_name,
    lat: evaluationResult.input_summary.village_lat,
    lng: evaluationResult.input_summary.village_lng,
    coord_precision: "approximate"
  } : null;

  return (
    <div className="app-shell">
      <Navbar onOpenWeights={() => setIsWeightsOpen(true)} />

      {/* Sticky Top Tab Bar */}
      <nav className="view-tabs-bar" aria-label="Views">
        <button
          type="button"
          className={`tab-btn ${activeTab === 'input' ? 'active' : ''}`}
          onClick={() => switchTab('input')}
        >
          1. Biomass & Village Origin
        </button>
        <button
          type="button"
          className={`tab-btn ${activeTab === 'pathways' ? 'active' : ''}`}
          onClick={() => switchTab('pathways')}
          disabled={!evaluationResult}
        >
          2. Ranked Pathways ({evaluationResult ? evaluationResult.eligible_count : 0})
        </button>
        <button
          type="button"
          className={`tab-btn ${activeTab === 'explanation' ? 'active' : ''}`}
          onClick={() => switchTab('explanation')}
          disabled={!evaluationResult}
        >
          3. Factor Breakdown
        </button>
        <button
          type="button"
          className={`tab-btn ${activeTab === 'map' ? 'active' : ''}`}
          onClick={() => switchTab('map')}
          disabled={!evaluationResult}
        >
          4. Map & Facilities ({evaluationResult ? evaluationResult.nearby_offtakers?.length : 0})
        </button>
        <button
          type="button"
          className={`tab-btn ${activeTab === 'compare' ? 'active' : ''}`}
          onClick={() => switchTab('compare')}
          disabled={!evaluationResult}
        >
          5. Constraints & Checklist
        </button>
      </nav>

      {/* Main Internally Scrolling Area */}
      <main className={`main-content ${activeTab === 'map' ? 'map-active' : ''}`}>
        {activeTab === 'input' && (
          <BiomassInputForm
            biomassTypes={biomassTypes}
            districts={districts}
            villages={villages}
            selectedDistrictId={selectedDistrictId}
            onDistrictChange={setSelectedDistrictId}
            onSubmit={handleRunEvaluation}
            loading={evalLoading}
            error={evalError}
          />
        )}

        {activeTab === 'pathways' && evaluationResult && (
          <PathwayList
            rankedPathways={evaluationResult.ranked_pathways}
            selectedPathwayId={selectedPathwayId}
            onSelectPathway={(id) => {
              setSelectedPathwayId(id);
              switchTab('explanation');
            }}
            eligibleCount={evaluationResult.eligible_count}
            ineligibleCount={evaluationResult.ineligible_count}
          />
        )}

        {activeTab === 'explanation' && evaluationResult && (
          <FactorBreakdown
            pathway={selectedPathway}
            missingInfo={evaluationResult.missing_info}
          />
        )}

        {activeTab === 'map' && evaluationResult && (
          <OfftakerMap
            originVillage={originVillage}
            nearbyOfftakers={evaluationResult.nearby_offtakers}
            nearbyHubs={evaluationResult.nearby_hubs}
            nearbyFarmerGroups={evaluationResult.nearby_farmer_groups}
            catchmentRadiusKm={evaluationResult.catchment_radius_km}
            selectedPathwayId={selectedPathwayId}
          />
        )}

        {activeTab === 'compare' && evaluationResult && (
          <CompareTable
            rankedPathways={evaluationResult.ranked_pathways}
            selectedPathwayId={selectedPathwayId}
            onSelectPathway={setSelectedPathwayId}
          />
        )}
      </main>

      {/* Footer Strip */}
      <footer className="footer-strip">
        <div>
          <strong>BioLoop Gujarat</strong> — Village-Level Agro-Residue Decision Support • Approximate Coordinates
        </div>
        <div>
          "A recommendation is not a guaranteed transaction. Verify with local participants."
        </div>
      </footer>

      {/* Factor Weights Drawer */}
      <WeightsDrawer
        isOpen={isWeightsOpen}
        onClose={() => setIsWeightsOpen(false)}
        weights={weights}
        onSaveWeights={handleSaveWeights}
      />
    </div>
  );
}
