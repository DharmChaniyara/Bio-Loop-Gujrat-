/**
 * API client for BioLoop Gujarat backend (village-level granularity).
 */
const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

async function handleResponse(res) {
  if (!res.ok) {
    let errorDetail = 'Network request failed';
    try {
      const data = await res.json();
      errorDetail = data.detail || JSON.stringify(data);
    } catch {
      errorDetail = `Status ${res.status}: ${res.statusText}`;
    }
    throw new Error(errorDetail);
  }
  return res.json();
}

export async function fetchBiomassTypes() {
  const res = await fetch(`${API_BASE}/api/biomass-types`);
  return handleResponse(res);
}

export async function fetchDistricts() {
  const res = await fetch(`${API_BASE}/api/districts`);
  return handleResponse(res);
}

export async function fetchVillages(districtId = '') {
  const url = districtId
    ? `${API_BASE}/api/villages?district_id=${encodeURIComponent(districtId)}`
    : `${API_BASE}/api/villages`;
  const res = await fetch(url);
  return handleResponse(res);
}

export async function fetchOfftakers(villageId = '', pathway = '', radiusKm = null) {
  const params = new URLSearchParams();
  if (villageId) params.append('village_id', villageId);
  if (pathway) params.append('pathway', pathway);
  if (radiusKm) params.append('radius_km', radiusKm.toString());
  const res = await fetch(`${API_BASE}/api/offtakers?${params.toString()}`);
  return handleResponse(res);
}

export async function fetchHubs(villageId = '', radiusKm = null) {
  const params = new URLSearchParams();
  if (villageId) params.append('village_id', villageId);
  if (radiusKm) params.append('radius_km', radiusKm.toString());
  const res = await fetch(`${API_BASE}/api/hubs?${params.toString()}`);
  return handleResponse(res);
}

export async function fetchFarmerGroups(villageId = '', radiusKm = null) {
  const params = new URLSearchParams();
  if (villageId) params.append('village_id', villageId);
  if (radiusKm) params.append('radius_km', radiusKm.toString());
  const res = await fetch(`${API_BASE}/api/farmer-groups?${params.toString()}`);
  return handleResponse(res);
}

export async function fetchWeights() {
  const res = await fetch(`${API_BASE}/api/weights`);
  return handleResponse(res);
}

export async function updateWeights(weightsMap) {
  const res = await fetch(`${API_BASE}/api/weights`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ weights: weightsMap }),
  });
  return handleResponse(res);
}

export async function evaluateBiomass(payload) {
  const res = await fetch(`${API_BASE}/api/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}
