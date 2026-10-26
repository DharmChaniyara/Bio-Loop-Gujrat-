import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, Circle, useMap } from 'react-leaflet';
import L from 'leaflet';

// Custom SVG marker icons
const createCustomIcon = (color, labelText) => {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="34" viewBox="0 0 30 38">
      <path d="M15 0 C6.7 0 0 6.7 0 15 C0 26.2 15 38 15 38 C15 38 30 26.2 30 15 C30 6.7 23.3 0 15 0 Z" fill="${color}" stroke="#1F2420" stroke-width="1.5"/>
      <circle cx="15" cy="14" r="5.5" fill="#F7F3EA" />
    </svg>
  `;
  return L.divIcon({
    className: 'custom-leaflet-pin',
    html: `<div style="display:flex;flex-direction:column;align-items:center;">
             ${svg}
             <span style="font-family:'IBM Plex Sans',sans-serif;font-size:10px;font-weight:600;background:#F7F3EA;border:1px solid #1F2420;padding:1px 3px;margin-top:-6px;white-space:nowrap;border-radius:2px;">
               ${labelText}
             </span>
           </div>`,
    iconSize: [28, 44],
    iconAnchor: [14, 34],
    popupAnchor: [0, -34],
  });
};

const offtakerIcon = createCustomIcon('#2D4A2F', 'Offtaker');
const hubIcon = createCustomIcon('#D4A843', 'Hub');
const farmerGroupIcon = createCustomIcon('#C4784F', 'Farmers');

// Map view flight controller
function MapFlyTo({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center && center.length === 2) {
      map.flyTo(center, 9, { duration: 0.8 });
    }
  }, [center, map]);
  return null;
}

export default function OfftakerMap({
  originVillage,
  nearbyOfftakers,
  nearbyHubs,
  nearbyFarmerGroups,
  catchmentRadiusKm,
  selectedPathwayId
}) {
  const [panelOpen, setPanelOpen] = useState(true);
  const [activeCategory, setActiveCategory] = useState('offtakers'); // 'offtakers' | 'hubs' | 'farmers'
  const [hoveredId, setHoveredId] = useState(null);

  const centerPos = originVillage
    ? [originVillage.lat, originVillage.lng]
    : [21.764, 72.152];

  const displayOfftakers = selectedPathwayId
    ? nearbyOfftakers.filter((o) => o.pathway_ids.includes(selectedPathwayId))
    : nearbyOfftakers;

  return (
    <div className="map-page-container">
      {/* Map Side Panel Toggle Button */}
      <button
        type="button"
        className={`btn btn-primary map-side-toggle ${panelOpen ? '' : 'collapsed'}`}
        onClick={() => setPanelOpen(!panelOpen)}
        style={{ padding: '6px 12px', fontSize: 'var(--text-xs)' }}
        aria-expanded={panelOpen}
      >
        {panelOpen ? 'Hide Facilities ❯' : '❮ View Facilities'}
      </button>

      {/* Edge-to-Edge Full-Bleed Map Viewport */}
      <div className="map-viewport">
        <MapContainer
          center={centerPos}
          zoom={9}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={true}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <MapFlyTo center={centerPos} />

          {/* Catchment Radius Boundary Circle */}
          {catchmentRadiusKm && (
            <Circle
              center={centerPos}
              radius={catchmentRadiusKm * 1000}
              pathOptions={{
                color: '#2D4A2F',
                fillColor: '#DDE3D3',
                fillOpacity: 0.12,
                weight: 1.5,
                dashArray: '4, 4'
              }}
            />
          )}

          {/* Origin Village Marker */}
          <CircleMarker
            center={centerPos}
            radius={8}
            pathOptions={{ color: '#1F2420', fillColor: '#C4784F', fillOpacity: 0.95, weight: 2 }}
          >
            <Popup>
              <div style={{ fontSize: '13px' }}>
                <strong>Origin: {originVillage ? originVillage.name : 'Gujarat'}</strong>
                <div style={{ fontSize: '11px', color: '#666', marginTop: '2px' }}>
                  Taluka: {originVillage?.taluka} • District: {originVillage?.district_id}
                </div>
                <div style={{ fontSize: '11px', color: '#888', marginTop: '3px' }}>
                  Approximate centroid ({originVillage?.coord_precision})
                </div>
              </div>
            </Popup>
          </CircleMarker>

          {/* Offtaker Facility Markers */}
          {displayOfftakers.map((off) => (
            <Marker
              key={off.id}
              position={[off.lat, off.lng]}
              icon={offtakerIcon}
            >
              <Popup>
                <div style={{ minWidth: '220px', fontSize: '13px' }}>
                  <div style={{ fontWeight: 600, color: 'var(--color-forest)', marginBottom: '3px' }}>
                    {off.name}
                  </div>
                  <div><strong>Type:</strong> {off.type}</div>
                  <div><strong>Village / Taluka:</strong> {off.village_name} ({off.district_name})</div>
                  <div><strong>Capacity:</strong> {off.capacity_tpm} t/month</div>
                  {off.distance_km !== null && (
                    <div style={{ marginTop: '3px' }}>
                      <strong>Haversine Distance:</strong>{' '}
                      <span style={{ color: 'var(--color-terracotta)', fontWeight: 600 }}>
                        {off.distance_km} km
                      </span>
                      {off.est_trip_time_mins && (
                        <span style={{ color: 'var(--color-ink-muted)', fontSize: '12px' }}>
                          {' '}(~{off.est_trip_time_mins} mins road estimate)
                        </span>
                      )}
                    </div>
                  )}
                  <div style={{ marginTop: '5px' }}>
                    <span className="badge-tag demo">
                      Status: {off.listing_status} (Illustrative only)
                    </span>
                  </div>
                  <div style={{ fontSize: '11px', color: '#666', marginTop: '5px', borderTop: '1px solid #ddd', paddingTop: '4px' }}>
                    <div><strong>Limitations:</strong> {off.limitations}</div>
                  </div>
                </div>
              </Popup>
            </Marker>
          ))}

          {/* Logistics Aggregation Hub Markers */}
          {nearbyHubs.map((hub) => (
            <Marker
              key={hub.id}
              position={[hub.lat, hub.lng]}
              icon={hubIcon}
            >
              <Popup>
                <div style={{ minWidth: '210px', fontSize: '13px' }}>
                  <div style={{ fontWeight: 600, color: '#8F6612', marginBottom: '3px' }}>
                    {hub.name}
                  </div>
                  <div><strong>Hub Role:</strong> {hub.hub_type}</div>
                  <div><strong>Village / Taluka:</strong> {hub.village_name} ({hub.district_name})</div>
                  {hub.distance_km !== null && (
                    <div style={{ marginTop: '3px' }}>
                      <strong>Haversine Distance:</strong>{' '}
                      <span style={{ color: 'var(--color-terracotta)', fontWeight: 600 }}>
                        {hub.distance_km} km
                      </span>
                      {hub.est_trip_time_mins && (
                        <span style={{ color: 'var(--color-ink-muted)', fontSize: '12px' }}>
                          {' '}(~{hub.est_trip_time_mins} mins)
                        </span>
                      )}
                    </div>
                  )}
                  <div style={{ marginTop: '5px' }}>
                    <span className="badge-tag demo">
                      Status: {hub.listing_status} (Demo)
                    </span>
                  </div>
                  <div style={{ fontSize: '11px', color: '#666', marginTop: '5px', borderTop: '1px solid #ddd', paddingTop: '4px' }}>
                    <div><strong>Limitations:</strong> {hub.limitations}</div>
                  </div>
                </div>
              </Popup>
            </Marker>
          ))}

          {/* Farmer Group Markers */}
          {nearbyFarmerGroups.map((fg) => {
            if (!fg.lat || !fg.lng) return null;
            return (
              <Marker
                key={fg.id}
                position={[fg.lat, fg.lng]}
                icon={farmerGroupIcon}
              >
                <Popup>
                  <div style={{ minWidth: '210px', fontSize: '13px' }}>
                    <div style={{ fontWeight: 600, color: '#A3532C', marginBottom: '3px' }}>
                      {fg.name}
                    </div>
                    <div><strong>Location:</strong> {fg.village_name} ({fg.district_name})</div>
                    <div><strong>Est. Supply:</strong> {fg.est_supply_tpm} t/month</div>
                    <div><strong>Season:</strong> {fg.season_months?.join(', ')}</div>
                    {fg.distance_km !== null && (
                      <div><strong>Distance:</strong> {fg.distance_km} km</div>
                    )}
                    <div style={{ marginTop: '5px' }}>
                      <span className="badge-tag demo">Demo FPO</span>
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>

      {/* Slim Collapsible Side Panel */}
      <aside className={`map-side-panel ${panelOpen ? '' : 'collapsed'}`}>
        <div style={{ padding: 'var(--space-3) var(--space-4)', borderBottom: '1px solid var(--color-border)', backgroundColor: 'var(--color-forest)', color: 'var(--color-cream)' }}>
          <div style={{ fontWeight: 600, fontSize: 'var(--text-base)' }}>Nearby Facilities & Logistics</div>
          <div style={{ fontSize: 'var(--text-xs)', color: '#CAD5C6', marginTop: '2px' }}>
            Catchment: {catchmentRadiusKm} km around {originVillage?.name || 'Village'}
          </div>
        </div>

        {/* Category Tabs */}
        <div style={{ display: 'flex', borderBottom: '1px solid var(--color-border)', backgroundColor: 'var(--color-cream)' }}>
          <button
            type="button"
            className="tab-btn"
            style={{
              flex: 1,
              borderRadius: 0,
              borderBottom: activeCategory === 'offtakers' ? '2px solid var(--color-forest)' : 'none',
              fontWeight: activeCategory === 'offtakers' ? 600 : 400,
              color: activeCategory === 'offtakers' ? 'var(--color-forest)' : 'var(--color-ink-muted)',
            }}
            onClick={() => setActiveCategory('offtakers')}
          >
            Offtakers ({displayOfftakers.length})
          </button>
          <button
            type="button"
            className="tab-btn"
            style={{
              flex: 1,
              borderRadius: 0,
              borderBottom: activeCategory === 'hubs' ? '2px solid var(--color-forest)' : 'none',
              fontWeight: activeCategory === 'hubs' ? 600 : 400,
              color: activeCategory === 'hubs' ? 'var(--color-forest)' : 'var(--color-ink-muted)',
            }}
            onClick={() => setActiveCategory('hubs')}
          >
            Hubs ({nearbyHubs.length})
          </button>
          <button
            type="button"
            className="tab-btn"
            style={{
              flex: 1,
              borderRadius: 0,
              borderBottom: activeCategory === 'farmers' ? '2px solid var(--color-forest)' : 'none',
              fontWeight: activeCategory === 'farmers' ? 600 : 400,
              color: activeCategory === 'farmers' ? 'var(--color-forest)' : 'var(--color-ink-muted)',
            }}
            onClick={() => setActiveCategory('farmers')}
          >
            Farmers ({nearbyFarmerGroups.length})
          </button>
        </div>

        {/* Scrollable Entity List */}
        <div style={{ flex: 1, overflowY: 'auto', padding: 'var(--space-3)' }}>
          {activeCategory === 'offtakers' && (
            displayOfftakers.length === 0 ? (
              <div style={{ padding: 'var(--space-4)', fontSize: 'var(--text-xs)', color: 'var(--color-ink-muted)', textAlign: 'center' }}>
                No off-takers found within {catchmentRadiusKm} km catchment radius. Try expanding the radius on the input form.
              </div>
            ) : (
              displayOfftakers.map((off) => (
                <div
                  key={off.id}
                  style={{
                    padding: 'var(--space-2) var(--space-3)',
                    backgroundColor: 'var(--color-cream)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-sm)',
                    marginBottom: 'var(--space-2)',
                    fontSize: 'var(--text-xs)',
                  }}
                  onMouseEnter={() => setHoveredId(off.id)}
                  onMouseLeave={() => setHoveredId(null)}
                >
                  <div style={{ fontWeight: 600, color: 'var(--color-forest)', fontSize: 'var(--text-sm)' }}>
                    {off.name}
                  </div>
                  <div>Location: {off.village_name} ({off.district_name})</div>
                  <div style={{ marginTop: '2px' }}>
                    <strong>Distance:</strong>{' '}
                    <span style={{ color: 'var(--color-terracotta)', fontWeight: 600 }}>
                      {off.distance_km} km
                    </span>
                    {off.est_trip_time_mins && (
                      <span> (~{off.est_trip_time_mins} mins)</span>
                    )}
                  </div>
                  <div style={{ marginTop: '4px' }}>
                    <span className="badge-tag demo">{off.type}</span>
                  </div>
                </div>
              ))
            )
          )}

          {activeCategory === 'hubs' && (
            nearbyHubs.length === 0 ? (
              <div style={{ padding: 'var(--space-4)', fontSize: 'var(--text-xs)', color: 'var(--color-ink-muted)', textAlign: 'center' }}>
                No aggregation hubs within {catchmentRadiusKm} km.
              </div>
            ) : (
              nearbyHubs.map((hub) => (
                <div
                  key={hub.id}
                  style={{
                    padding: 'var(--space-2) var(--space-3)',
                    backgroundColor: 'var(--color-cream)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-sm)',
                    marginBottom: 'var(--space-2)',
                    fontSize: 'var(--text-xs)',
                  }}
                >
                  <div style={{ fontWeight: 600, color: '#8F6612', fontSize: 'var(--text-sm)' }}>
                    {hub.name}
                  </div>
                  <div>Type: {hub.hub_type} • Location: {hub.village_name}</div>
                  <div style={{ marginTop: '2px' }}>
                    <strong>Distance:</strong> {hub.distance_km} km (~{hub.est_trip_time_mins} mins)
                  </div>
                </div>
              ))
            )
          )}

          {activeCategory === 'farmers' && (
            nearbyFarmerGroups.length === 0 ? (
              <div style={{ padding: 'var(--space-4)', fontSize: 'var(--text-xs)', color: 'var(--color-ink-muted)', textAlign: 'center' }}>
                No registered farmer groups in radius.
              </div>
            ) : (
              nearbyFarmerGroups.map((fg) => (
                <div
                  key={fg.id}
                  style={{
                    padding: 'var(--space-2) var(--space-3)',
                    backgroundColor: 'var(--color-cream)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-sm)',
                    marginBottom: 'var(--space-2)',
                    fontSize: 'var(--text-xs)',
                  }}
                >
                  <div style={{ fontWeight: 600, color: '#A3532C', fontSize: 'var(--text-sm)' }}>
                    {fg.name}
                  </div>
                  <div>Location: {fg.village_name} • Est Supply: {fg.est_supply_tpm} t/mo</div>
                  <div style={{ marginTop: '2px' }}>
                    <strong>Distance:</strong> {fg.distance_km} km
                  </div>
                </div>
              ))
            )
          )}
        </div>
      </aside>
    </div>
  );
}
