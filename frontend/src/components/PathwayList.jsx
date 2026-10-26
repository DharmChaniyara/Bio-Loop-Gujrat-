import React from 'react';

export default function PathwayList({
  rankedPathways,
  selectedPathwayId,
  onSelectPathway,
  eligibleCount,
  ineligibleCount
}) {
  return (
    <div className="view-panel-enter">
      <div className="view-header">
        <div className="view-title-wrap">
          <div className="title-accent-rule"></div>
          <h2>Ranked Utilization Pathways</h2>
        </div>
        <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
          <span className="badge-tag verified">{eligibleCount} Eligible</span>
          {ineligibleCount > 0 && (
            <span className="badge-tag demo">{ineligibleCount} Ineligible</span>
          )}
        </div>
      </div>

      <div className="callout-box">
        <p>
          Rankings are calculated strictly from weighted factor contributions from the village origin.
          Click any pathway row to inspect its 5-factor breakdown and engineering parameters.
        </p>
      </div>

      <div className="data-table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: '50px' }}>Rank</th>
              <th>Pathway Name</th>
              <th style={{ width: '90px' }}>Score</th>
              <th style={{ width: '130px' }}>Confidence</th>
              <th>Logistics & Fit Rationale</th>
              <th style={{ width: '90px' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {rankedPathways.map((p, idx) => {
              const isSelected = p.pathway_id === selectedPathwayId;
              const confidenceClass = p.data_confidence.toLowerCase();

              return (
                <tr
                  key={p.pathway_id}
                  className="stagger-item"
                  style={{
                    animationDelay: `${idx * 40}ms`,
                    backgroundColor: isSelected
                      ? 'var(--color-sage)'
                      : !p.eligible
                      ? '#F9F6F0'
                      : undefined,
                    opacity: !p.eligible ? 0.75 : 1,
                  }}
                >
                  <td style={{ fontWeight: 600 }}>
                    {p.eligible ? `#${p.rank}` : '—'}
                  </td>
                  <td>
                    <div style={{ fontWeight: 600, color: 'var(--color-forest)' }}>
                      {p.pathway_name}
                    </div>
                    <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-ink-muted)', marginTop: '2px' }}>
                      Capex: {p.capex_level} • Ease: {p.ease_level}
                    </div>
                  </td>
                  <td style={{ fontWeight: 700, fontSize: 'var(--text-md)', color: p.eligible ? 'var(--color-terracotta)' : 'var(--color-ink-muted)' }}>
                    {p.eligible ? `${p.score}/100` : '0/100'}
                  </td>
                  <td>
                    <span className={`badge-tag ${confidenceClass}`}>
                      {p.data_confidence}
                    </span>
                  </td>
                  <td style={{ fontSize: 'var(--text-sm)' }}>
                    {p.status_reason}
                    {!p.eligible && p.ineligibility_reasons.length > 0 && (
                      <div style={{ color: 'var(--color-danger)', fontSize: 'var(--text-xs)', marginTop: '4px' }}>
                        Reason: {p.ineligibility_reasons[0]}
                      </div>
                    )}
                  </td>
                  <td>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      style={{
                        padding: '3px 8px',
                        fontSize: 'var(--text-xs)',
                        backgroundColor: isSelected ? 'var(--color-forest)' : undefined,
                        color: isSelected ? 'var(--color-cream)' : undefined,
                      }}
                      onClick={() => onSelectPathway(p.pathway_id)}
                    >
                      {isSelected ? 'Viewing' : 'Inspect'}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
