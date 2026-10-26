import React from 'react';

export default function FactorBreakdown({ pathway, missingInfo }) {
  if (!pathway) {
    return (
      <div className="view-panel-enter">
        <div className="view-header">
          <div className="view-title-wrap">
            <div className="title-accent-rule"></div>
            <h2>Pathway Factor Breakdown</h2>
          </div>
        </div>
        <p style={{ color: 'var(--color-ink-muted)' }}>
          Select a pathway from the Ranked Pathways table to see its factor breakdown.
        </p>
      </div>
    );
  }

  const getStatusBadgeClass = (status) => {
    if (status === 'Verified') return 'verified';
    if (status === 'Requires verification') return 'requires-verification';
    return 'demo';
  };

  return (
    <div className="view-panel-enter">
      <div className="view-header">
        <div className="view-title-wrap">
          <div className="title-accent-rule"></div>
          <h2>Why "{pathway.pathway_name}" Ranked Here</h2>
        </div>
        <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center' }}>
          <span style={{ fontSize: 'var(--text-sm)', color: 'var(--color-ink-muted)' }}>Overall Score:</span>
          <span style={{ fontSize: 'var(--text-xl)', fontWeight: 700, color: 'var(--color-terracotta)' }}>
            {pathway.score}/100
          </span>
          <span className={`badge-tag ${pathway.data_confidence.toLowerCase()}`}>
            Confidence: {pathway.data_confidence}
          </span>
        </div>
      </div>

      <div style={{ marginBottom: 'var(--space-4)', fontSize: 'var(--text-sm)' }}>
        <strong>Summary Reason:</strong> {pathway.status_reason}
      </div>

      {/* Factor Breakdown Table */}
      <h3 style={{ fontSize: 'var(--text-md)', marginBottom: 'var(--space-3)' }}>
        Weighted Factor Contribution Breakdown
      </h3>

      <div className="data-table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>Evaluation Factor</th>
              <th style={{ width: '80px' }}>Weight</th>
              <th style={{ width: '90px' }}>Raw (0-100)</th>
              <th style={{ width: '100px' }}>Weighted</th>
              <th style={{ width: '160px' }}>Status</th>
              <th>Assessment Logic</th>
            </tr>
          </thead>
          <tbody>
            {pathway.factors.map((f, idx) => (
              <tr key={idx} className="stagger-item" style={{ animationDelay: `${idx * 40}ms` }}>
                <td style={{ fontWeight: 600 }}>{f.factor_name}</td>
                <td>{(f.weight * 100).toFixed(0)}%</td>
                <td style={{ fontWeight: 600 }}>
                  {f.raw_score.toFixed(1)}
                  <div className="factor-bar-bg">
                    <div
                      className="factor-bar-fill"
                      style={{ width: `${Math.min(100, f.raw_score)}%` }}
                    />
                  </div>
                </td>
                <td style={{ fontWeight: 700, color: 'var(--color-forest)' }}>
                  +{f.weighted_score.toFixed(1)}
                </td>
                <td>
                  <span className={`badge-tag ${getStatusBadgeClass(f.status)}`}>
                    {f.status}
                  </span>
                </td>
                <td style={{ fontSize: 'var(--text-xs)', lineHeight: 1.4 }}>
                  {f.explanation}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Explicit Missing Information Box */}
      {missingInfo && missingInfo.length > 0 && (
        <div className="callout-box" style={{ borderLeftColor: '#B58428', backgroundColor: 'var(--color-warning-bg)', marginTop: 'var(--space-4)' }}>
          <div style={{ fontWeight: 600, marginBottom: 'var(--space-1)', color: '#825615' }}>
            Explicit Missing Information & Verification Needs:
          </div>
          <ul style={{ paddingLeft: 'var(--space-4)', fontSize: 'var(--text-xs)', margin: 0 }}>
            {missingInfo.map((item, i) => (
              <li key={i} style={{ marginBottom: '2px' }}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Source, Limitations & Record Status */}
      <div
        style={{
          marginTop: 'var(--space-4)',
          padding: 'var(--space-3) var(--space-4)',
          backgroundColor: 'var(--color-warm-paper)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-sm)',
          fontSize: 'var(--text-xs)',
          color: 'var(--color-ink-muted)',
        }}
      >
        <div><strong>Record Status:</strong> <span className="badge-tag demo">{pathway.record_status}</span></div>
        <div><strong>Source Reference:</strong> {pathway.source}</div>
        <div><strong>Known Technical Limitations:</strong> {pathway.limitations}</div>
      </div>
    </div>
  );
}
