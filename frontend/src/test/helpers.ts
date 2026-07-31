import type { CartItem, GridData, Product, RouteResponse, Store } from '../types';

export function makeStore(overrides: Partial<Store> = {}): Store {
  return {
    id: 'store-1',
    name: 'Test Store',
    ...overrides,
  };
}

export function makeProduct(overrides: Partial<Product> = {}): Product {
  return {
    id: 'prod-1',
    name: 'Apple',
    price: 1.5,
    x: 4,
    y: 0,
    store_id: 'store-1',
    ...overrides,
  };
}

export function makeCartItem(overrides: Partial<CartItem> = {}): CartItem {
  return {
    product: makeProduct(),
    quantity: 1,
    ...overrides,
  };
}

export function makeGrid(): GridData {
  const cells = [];
  for (let y = 0; y < 3; y++) {
    for (let x = 0; x < 3; x++) {
      cells.push({ x, y, path: true, robot_start: x === 0 && y === 0 });
    }
  }
  return { width: 3, height: 3, cells };
}

export function makeRoute(overrides: Partial<RouteResponse> = {}): RouteResponse {
  return {
    visit_order: [{ x: 1, y: 0 }],
    cells: [{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 0, y: 0 }],
    total_seconds: 2,
    total_price: 1.5,
    exact: true,
    ...overrides,
  };
}
