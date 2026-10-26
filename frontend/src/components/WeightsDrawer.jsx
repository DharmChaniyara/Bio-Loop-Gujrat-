import React, { useState } from 'react';

export default function WeightsDrawer({ isOpen, onClose, weights, onSaveWeights }) {
  if (!isOpen) return null;

  const [formWeights, setFormWeights] = useState(() => {
    const map = {};
    weights.forEach((w) => {
      map[w.key] = w.value;
    });
    return map;
  });
  const [error, setError] = useState(null);

  const currentSum = Object.values(formWeights).reduce((a, b) => a + Number(b || 0), 0);

  const handleChange = (key, val) => {
    const num = parseFloat(val);
    setFormWeights((prev) => ({
      ...prev,
      [key]: isNaN(num) ? 0 : num,
    }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (Math.abs(currentSum - 1.0) > 0.005) {
      setError(`Weights must sum to 1.00 (currently ${currentSum.toFixed(3)})`);
      return;
    }
    setError(null);
    try {
      await onSaveWeights(formWeights);
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to update weights');
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(31, 36, 32, 0.45)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 9999,
        padding: '16px',
      }}
    >
      <div
        className="paper-panel"
        style={{
          maxWidth: '560px',
          width: '100%',
          maxHeight: '90vh',
          overflowY: 'auto',
          margin: 0,
          border: '2px solid var(--color-forest)',
        }}
      >
        <div className="view-header">
          <div className="view-title-wrap">
            <div className="title-accent-rule"></div>
            <h2>Evaluation Factor Weights</h2>
          </div>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onClose}
            style={{ padding: '2px 8px' }}
          >
            ✕
          </button>
        </div>

        <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-ink-muted)', marginBottom: 'var(--space-4)' }}>
          Adjust the relative weightings used by the deterministic scoring engine.
          The total sum must equal <strong>1.00</strong>.
        </p>

        {error && (
          <div className="callout-box" style={{ borderLeftColor: 'var(--color-danger)', backgroundColor: 'var(--color-danger-bg)', marginBottom: 'var(--space-4)' }}>
            <p><strong>Validation Error:</strong> {error}</p>
          </div>
        )}

        <form onSubmit={handleSave}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
            {weights.map((w) => (
              <div
                key={w.key}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: 'var(--space-3)',
                  padding: 'var(--space-2) var(--space-3)',
                  backgroundColor: 'var(--color-cream)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-sm)',
                }}
              >
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: 'var(--text-sm)' }}>
                    {w.key.replace(/^w\d+_/, '').replace(/_/g, ' ').toUpperCase()}
                  </div>
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-ink-muted)' }}>
                    {w.description}
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <input
                    type="number"
                    step="0.05"
                    min="0"
                    max="1"
                    className="field-input tabular-nums"
                    style={{ width: '80px', padding: '4px 6px', textAlign: 'right' }}
                    value={formWeights[w.key] ?? w.value}
                    onChange={(e) => handleChange(w.key, e.target.value)}
                  />
                </div>
              </div>
            ))}
          </div>

          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: 'var(--space-2) var(--space-3)',
              backgroundColor: Math.abs(currentSum - 1.0) <= 0.005 ? 'var(--color-success-bg)' : 'var(--color-danger-bg)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-sm)',
              marginBottom: 'var(--space-5)',
              fontSize: 'var(--text-sm)',
              fontWeight: 600,
            }}
          >
            <span>Total Weight Sum:</span>
            <span className="tabular-nums" style={{ color: Math.abs(currentSum - 1.0) <= 0.005 ? 'var(--color-forest)' : 'var(--color-danger)' }}>
              {currentSum.toFixed(3)} / 1.000
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-3)' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={Math.abs(currentSum - 1.0) > 0.005}
            >
              Apply Weights
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
