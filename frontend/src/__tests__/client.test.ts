import { describe, expect, it, vi, beforeEach } from 'vitest';
import { ApiError, getStores, getStoreProducts, getGrid, calculateRoute } from '../api/client';

// Mock import.meta.env
vi.stubEnv('VITE_API_URL', 'http://localhost:8000');

const mockFetch = vi.fn();
globalThis.fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockReset();
});

function okResponse(data: unknown) {
  return {
    ok: true,
    json: () => Promise.resolve(data),
  };
}

function errorResponse(status: number, body: Record<string, unknown>) {
  return {
    ok: false,
    status,
    statusText: 'Error',
    json: () => Promise.resolve(body),
  };
}

describe('ApiError', () => {
  it('has status, message, and body', () => {
    const err = new ApiError(404, 'Not found', { detail: 'Not found' });
    expect(err.status).toBe(404);
    expect(err.message).toBe('Not found');
    expect(err.body).toEqual({ detail: 'Not found' });
    expect(err.name).toBe('ApiError');
  });
});

describe('getStores', () => {
  it('fetches stores from API', async () => {
    const stores = [{ id: 's1', name: 'Store A' }];
    mockFetch.mockResolvedValue(okResponse(stores));
    const result = await getStores();
    expect(result).toEqual(stores);
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/stores',
      undefined,
    );
  });

  it('throws ApiError on failure', async () => {
    mockFetch.mockResolvedValue(errorResponse(500, { detail: 'Server error' }));
    await expect(getStores()).rejects.toThrow(ApiError);
  });
});

describe('getStoreProducts', () => {
  it('fetches products for a store', async () => {
    const products = [{ id: 'p1', name: 'Apple' }];
    mockFetch.mockResolvedValue(okResponse(products));
    const result = await getStoreProducts('s1');
    expect(result).toEqual(products);
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/stores/s1/products',
      undefined,
    );
  });
});

describe('getGrid', () => {
  it('fetches grid', async () => {
    const grid = { width: 5, height: 5, cells: [] };
    mockFetch.mockResolvedValue(okResponse(grid));
    const result = await getGrid();
    expect(result).toEqual(grid);
  });
});

describe('calculateRoute', () => {
  it('posts product IDs and returns route', async () => {
    const route = {
      visit_order: [{ x: 1, y: 0 }],
      cells: [{ x: 0, y: 0 }, { x: 1, y: 0 }],
      total_seconds: 1,
      total_price: 1.5,
      exact: true,
    };
    mockFetch.mockResolvedValue(okResponse(route));
    const result = await calculateRoute(['id-1']);
    expect(result).toEqual(route);
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/route',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_ids: ['id-1'] }),
      },
    );
  });

  it('throws ApiError with status on 409', async () => {
    mockFetch.mockResolvedValue(
      errorResponse(409, { detail: 'Unreachable products' }),
    );
    try {
      await calculateRoute(['id-1']);
      expect.fail('should have thrown');
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError);
      expect((err as ApiError).status).toBe(409);
    }
  });
});
