import React from 'react';

export default function Navbar({ onOpenWeights }) {
  return (
    <header className="top-nav">
      <div className="nav-inner">
        <div className="brand-wrap">
          <div className="brand-title">BioLoop Gujarat</div>
          <span
            className="badge-tag demo"
            style={{
              borderColor: 'var(--color-ochre)',
              color: 'var(--color-cream)',
              backgroundColor: 'transparent',
            }}
          >
            Demo data
          </span>
          <span className="brand-subtitle" style={{ display: 'none' }}>
            Decision Support
          </span>
        </div>

        <div>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onOpenWeights}
            style={{
              color: 'var(--color-cream)',
              borderColor: '#607C62',
              padding: '4px 10px',
              fontSize: 'var(--text-xs)',
            }}
            title="Inspect and adjust evaluation factor weights"
          >
            ⚙ Factor Weights
          </button>
        </div>
      </div>
    </header>
  );
}
