import React, { useState, useEffect } from 'react';

export default function BiomassInputForm({
  biomassTypes,
  districts,
  villages,
  selectedDistrictId,
  onDistrictChange,
  onSubmit,
  loading,
  error
}) {
  const [biomassType, setBiomassType] = useState('groundnut_shell');
  const [villageId, setVillageId] = useState('talaja');
  const [quantity, setQuantity] = useState('120');
  const [moisture, setMoisture] = useState('11');
  const [radiusKm, setRadiusKm] = useState('100');
  const [seasonality, setSeasonality] = useState('Post-Kharif harvest shells available November through February.');
  const [validationErrors, setValidationErrors] = useState({});

  // When villages list changes, ensure a valid village is selected
  useEffect(() => {
    if (villages && villages.length > 0) {
      const match = villages.find((v) => v.id === villageId);
      if (!match) {
        setVillageId(villages[0].id);
      }
    }
  }, [villages]);

  const selectedBiomassObj = biomassTypes.find((b) => b.id === biomassType);
  const selectedVillageObj = villages.find((v) => v.id === villageId);
  const selectedDistrictObj = districts.find((d) => d.id === selectedDistrictId);

  const handleSubmit = (e) => {
    e.preventDefault();
    const errors = {};

    const qNum = parseFloat(quantity);
    if (isNaN(qNum) || qNum <= 0) {
      errors.quantity = 'Quantity must be a positive number greater than 0.';
    }

    let mNum = null;
    if (moisture !== '') {
      mNum = parseFloat(moisture);
      if (isNaN(mNum) || mNum < 0 || mNum > 100) {
        errors.moisture = 'Moisture must be between 0% and 100%.';
      }
    }

    if (!biomassType) {
      errors.biomassType = 'Select a biomass type.';
    }

    if (!villageId) {
      errors.villageId = 'Select a village or taluka.';
    }

    setValidationErrors(errors);

    if (Object.keys(errors).length === 0) {
      onSubmit({
        biomass_type: biomassType,
        district_id: selectedDistrictId,
        village_id: villageId,
        quantity: qNum,
        moisture_content: mNum,
        seasonality_notes: seasonality.trim() || null,
        max_radius_km: parseFloat(radiusKm) || 100.0,
      });
    }
  };

  const handleApplyPreset = () => {
    onDistrictChange('bhavnagar');
    setBiomassType('groundnut_shell');
    setVillageId('talaja');
    setQuantity('120');
    setMoisture('11');
    setRadiusKm('100');
    setSeasonality('Post-Kharif harvest shells available November through February.');
    setValidationErrors({});
  };

  return (
    <div className="view-panel-enter">
      <div className="view-header">
        <div className="view-title-wrap">
          <div className="title-accent-rule"></div>
          <h2>Enter Biomass & Village Origin</h2>
        </div>
        <span className="badge-tag demo">Field Evaluation Form</span>
      </div>

      <div className="inputs-two-col">
        {/* Left Column: Input Form */}
        <div className="paper-panel" style={{ margin: 0 }}>
          <div className="callout-box">
            <p>
              <strong>Evaluation principle:</strong> Evaluates viability using engineering thresholds
              and straight-line Haversine distance with rural road transit estimates.
              There is <strong>no AI/LLM</strong> in the scoring path.
            </p>
          </div>

          {error && (
            <div className="callout-box" style={{ borderLeftColor: 'var(--color-danger)', backgroundColor: 'var(--color-danger-bg)' }}>
              <p><strong>Evaluation Error:</strong> {error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate>
            <div className="form-grid">
              {/* Biomass Type (Readable options with secondary text, no truncation) */}
              <div className="field-group" style={{ gridColumn: '1 / -1' }}>
                <label className="field-label" htmlFor="biomass-select">
                  Biomass Feedstock Type *
                </label>
                <div className="field-hint">Select the agricultural residue or agro-industrial by-product</div>
                <select
                  id="biomass-select"
                  className="field-select"
                  value={biomassType}
                  onChange={(e) => setBiomassType(e.target.value)}
                >
                  {biomassTypes.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.name} — {b.category}
                    </option>
                  ))}
                </select>
                {validationErrors.biomassType && (
                  <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-danger)' }}>{validationErrors.biomassType}</span>
                )}
              </div>

              {/* District */}
              <div className="field-group">
                <label className="field-label" htmlFor="district-select">
                  1. District *
                </label>
                <div className="field-hint">Filters available talukas/villages</div>
                <select
                  id="district-select"
                  className="field-select"
                  value={selectedDistrictId}
                  onChange={(e) => onDistrictChange(e.target.value)}
                >
                  {districts.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name} ({d.region})
                    </option>
                  ))}
                </select>
              </div>

              {/* Village Selector (Depends on District) */}
              <div className="field-group">
                <label className="field-label" htmlFor="village-select">
                  2. Village / Taluka Origin *
                </label>
                <div className="field-hint">Origin coordinates for logistics</div>
                <select
                  id="village-select"
                  className="field-select"
                  value={villageId}
                  onChange={(e) => setVillageId(e.target.value)}
                >
                  {villages.map((v) => (
                    <option key={v.id} value={v.id}>
                      {v.name} (Taluka: {v.taluka})
                    </option>
                  ))}
                </select>
                {validationErrors.villageId && (
                  <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-danger)' }}>{validationErrors.villageId}</span>
                )}
              </div>

              {/* Quantity */}
              <div className="field-group">
                <label className="field-label" htmlFor="quantity-input">
                  Available Quantity (tonnes/month) *
                </label>
                <div className="field-hint">Monthly aggregate available for dispatch</div>
                <input
                  id="quantity-input"
                  type="number"
                  step="any"
                  className="field-input"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  placeholder="e.g. 120"
                  required
                />
                {validationErrors.quantity && (
                  <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-danger)' }}>{validationErrors.quantity}</span>
                )}
              </div>

              {/* Moisture */}
              <div className="field-group">
                <label className="field-label" htmlFor="moisture-input">
                  Moisture Content (%) (Optional)
                </label>
                <div className="field-hint">Leave blank if lab test is pending</div>
                <input
                  id="moisture-input"
                  type="number"
                  step="0.1"
                  className="field-input"
                  value={moisture}
                  onChange={(e) => setMoisture(e.target.value)}
                  placeholder="e.g. 11.0"
                />
                {validationErrors.moisture && (
                  <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-danger)' }}>{validationErrors.moisture}</span>
                )}
              </div>

              {/* Catchment Radius */}
              <div className="field-group" style={{ gridColumn: '1 / -1' }}>
                <label className="field-label" htmlFor="radius-select">
                  Catchment Logistics Radius (km)
                </label>
                <div className="field-hint">Maximum search radius for processing off-takers and hubs</div>
                <select
                  id="radius-select"
                  className="field-select"
                  value={radiusKm}
                  onChange={(e) => setRadiusKm(e.target.value)}
                >
                  <option value="25">25 km — Immediate local catchment</option>
                  <option value="50">50 km — Sub-district trucking radius</option>
                  <option value="100">100 km — Regional agricultural belt (Recommended)</option>
                  <option value="150">150 km — Cross-district haulage</option>
                </select>
              </div>
            </div>

            {/* Seasonality / Notes */}
            <div className="field-group" style={{ marginBottom: 'var(--space-5)' }}>
              <label className="field-label" htmlFor="seasonality-input">
                Seasonality & Storage Notes (Optional)
              </label>
              <div className="field-hint">
                Harvest window, covered shed availability, or threshing condition
              </div>
              <textarea
                id="seasonality-input"
                rows={2}
                className="field-textarea"
                value={seasonality}
                onChange={(e) => setSeasonality(e.target.value)}
                placeholder="e.g. Available Nov to Feb post-Kharif; stored in open yard."
              />
            </div>

            <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'center', flexWrap: 'wrap' }}>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? 'Evaluating...' : 'Run evaluation'}
              </button>

              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleApplyPreset}
              >
                Load Bhavnagar → Talaja Preset
              </button>
            </div>
          </form>
        </div>

        {/* Right Column: Live Context & Selected Origin Summary */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          {selectedVillageObj && (
            <div className="paper-panel" style={{ margin: 0 }}>
              <h3 style={{ fontSize: 'var(--text-base)', marginBottom: 'var(--space-2)' }}>
                Selected Village / Taluka Origin
              </h3>
              <div style={{ fontSize: 'var(--text-sm)', lineHeight: 1.6 }}>
                <div><strong>Location:</strong> {selectedVillageObj.name}, Taluka: {selectedVillageObj.taluka}</div>
                <div><strong>District:</strong> {selectedDistrictObj?.name || selectedVillageObj.district_id} ({selectedDistrictObj?.region || 'Gujarat'})</div>
                <div><strong>Coordinates:</strong> {selectedVillageObj.lat.toFixed(3)}°N, {selectedVillageObj.lng.toFixed(3)}°E</div>
                <div style={{ marginTop: '4px' }}>
                  <span className="badge-tag demo">
                    Precision: {selectedVillageObj.coord_precision}
                  </span>
                </div>
                <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-ink-muted)', marginTop: '6px' }}>
                  {selectedVillageObj.limitations}
                </div>
              </div>
            </div>
          )}

          {selectedBiomassObj && (
            <div className="paper-panel" style={{ margin: 0 }}>
              <h3 style={{ fontSize: 'var(--text-base)', marginBottom: 'var(--space-2)' }}>
                Feedstock Technical Baseline
              </h3>
              <div style={{ fontSize: 'var(--text-sm)', lineHeight: 1.6 }}>
                <div><strong>Feedstock:</strong> {selectedBiomassObj.name}</div>
                <div><strong>Typical Moisture:</strong> {selectedBiomassObj.typical_moisture_min}% – {selectedBiomassObj.typical_moisture_max}%</div>
                <div><strong>Harvest Months:</strong> {selectedBiomassObj.harvest_months?.join(', ')}</div>
                <div style={{ marginTop: '6px', fontSize: 'var(--text-xs)', color: 'var(--color-ink-muted)' }}>
                  <div><strong>Source:</strong> {selectedBiomassObj.source}</div>
                  <div><strong>Known Limitations:</strong> {selectedBiomassObj.limitations}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
