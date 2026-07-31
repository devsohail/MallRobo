import type { GridData, Product, RouteResponse, Store } from '../types';

const API_URL = import.meta.env.VITE_API_URL as string;

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new ApiError(response.status, body.detail ?? 'Request failed', body);
  }
  return response.json() as Promise<T>;
}

export class ApiError extends Error {
  status: number;
  body: Record<string, unknown>;

  constructor(status: number, message: string, body: Record<string, unknown> = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}

export function getStores(): Promise<Store[]> {
  return fetchJson<Store[]>(`${API_URL}/api/stores`);
}

export function getStoreProducts(storeId: string): Promise<Product[]> {
  return fetchJson<Product[]>(`${API_URL}/api/stores/${storeId}/products`);
}

export function getGrid(): Promise<GridData> {
  return fetchJson<GridData>(`${API_URL}/api/grid`);
}

export function calculateRoute(productIds: string[]): Promise<RouteResponse> {
  return fetchJson<RouteResponse>(`${API_URL}/api/route`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_ids: productIds }),
  });
}
