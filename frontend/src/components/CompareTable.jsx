import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';

export default function CompareTable({ rankedPathways, selectedPathwayId, onSelectPathway }) {
  const chartData = rankedPathways.map((p) => ({
    name: p.pathway_name.replace(' (White Coal)', '').replace(' (Industrial Fuel)', '').replace(' (Slow Pyrolysis)', ''),
    score: p.eligible ? p.score : 0,
    eligible: p.eligible,
    id: p.pathway_id,
  }));

  const selectedPathway = rankedPathways.find((p) => p.pathway_id === selectedPathwayId) || rankedPathways[0];

  return (
    <div className="view-panel-enter">
      <div className="view-header">
        <div className="view-title-wrap">
          <div className="title-accent-rule"></div>
          <h2>Compare Pathways & Next Steps</h2>
        </div>
        <span className="badge-tag verified">Multi-Factor Analysis</span>
      </div>

      <div className="callout-box" style={{ marginBottom: 'var(--space-5)' }}>
        <p>
          <strong>Notice:</strong> A recommendation is not a guaranteed transaction.
          Verify with local participants before entering commercial agreements.
        </p>
      </div>

      {/* Recharts Bar Chart */}
      <h3 style={{ fontSize: 'var(--text-md)', marginBottom: 'var(--space-3)' }}>
        Pathway Viability Scores Comparison
      </h3>
      <div style={{ width: '100%', height: 260, backgroundColor: 'var(--color-cream)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', padding: '16px 8px 8px 0', marginBottom: 'var(--space-5)' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 25 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#D8CFBE" />
            <XAxis
              dataKey="name"
              stroke="#565C56"
              fontSize={12}
              tickLine={false}
              interval={0}
              angle={-15}
              textAnchor="end"
            />
            <YAxis
              domain={[0, 100]}
              stroke="#565C56"
              fontSize={12}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#F7F3EA',
                borderColor: '#8F8778',
                borderRadius: '2px',
                fontSize: '13px',
                color: '#1F2420',
              }}
              formatter={(value) => [`${value}/100`, 'Viability Score']}
            />
            <Bar dataKey="score" radius={[2, 2, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.eligible ? (entry.id === selectedPathwayId ? '#C4784F' : '#2D4A2F') : '#8F8778'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Practical Constraints Comparison Table */}
      <h3 style={{ fontSize: 'var(--text-md)', marginBottom: 'var(--space-3)' }}>
        Practical Constraints Matrix
      </h3>

      <div className="data-table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>Pathway</th>
              <th style={{ width: '100px' }}>Capex</th>
              <th style={{ width: '160px' }}>Logistics Level</th>
              <th style={{ width: '120px' }}>Market Fit</th>
              <th style={{ width: '110px' }}>Ease Level</th>
              <th style={{ width: '100px' }}>Overall Score</th>
            </tr>
          </thead>
          <tbody>
            {rankedPathways.map((p) => {
              const isSelected = p.pathway_id === selectedPathwayId;
              return (
                <tr
                  key={p.pathway_id}
                  onClick={() => onSelectPathway(p.pathway_id)}
                  style={{
                    cursor: 'pointer',
                    backgroundColor: isSelected ? 'var(--color-sage)' : undefined,
                  }}
                >
                  <td style={{ fontWeight: 600 }}>
                    {p.pathway_name}
                    {!p.eligible && (
                      <span className="badge-tag demo" style={{ marginLeft: '6px', fontSize: '10px' }}>
                        Ineligible
                      </span>
                    )}
                  </td>
                  <td>{p.capex_level}</td>
                  <td>{p.logistics_level}</td>
                  <td>{p.market_fit_level}</td>
                  <td>{p.ease_level}</td>
                  <td style={{ fontWeight: 700, color: p.eligible ? 'var(--color-terracotta)' : 'var(--color-ink-muted)' }}>
                    {p.eligible ? `${p.score}/100` : '0/100'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Suggested Verification Steps Checklist */}
      {selectedPathway && (
        <div style={{ marginTop: 'var(--space-5)' }}>
          <h3 style={{ fontSize: 'var(--text-md)', marginBottom: 'var(--space-2)' }}>
            Suggested Verification & Next Steps for "{selectedPathway.pathway_name}"
          </h3>
          <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-ink-muted)', marginBottom: 'var(--space-3)' }}>
            Complete the following verification steps prior to finalizing transportation or supply agreements:
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
            {selectedPathway.verification_steps.map((step, idx) => (
              <label
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 'var(--space-3)',
                  padding: 'var(--space-2) var(--space-3)',
                  backgroundColor: 'var(--color-cream)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: 'var(--text-sm)',
                  cursor: 'pointer',
                }}
              >
                <input
                  type="checkbox"
                  style={{ marginTop: '3px', accentColor: 'var(--color-forest)' }}
                />
                <span>{step}</span>
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
