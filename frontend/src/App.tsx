import { useCallback, useEffect, useRef, useState } from 'react';
import { calculateRoute, getGrid } from './api/client';
import type { ApiError } from './api/client';
import { Cart } from './components/Cart';
import { GridCanvas } from './components/GridCanvas';
import { ProductList } from './components/ProductList';
import { RouteSummary } from './components/RouteSummary';
import { StoreSelector } from './components/StoreSelector';
import type { CartItem, GridData, Product, RouteResponse } from './types';

function App() {
  const [selectedStoreId, setSelectedStoreId] = useState<string | null>(null);
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [grid, setGrid] = useState<GridData | null>(null);
  const [route, setRoute] = useState<RouteResponse | null>(null);
  const [routeLoading, setRouteLoading] = useState(false);
  const [routeError, setRouteError] = useState<string | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Load grid on mount
  useEffect(() => {
    getGrid()
      .then(setGrid)
      .catch((err: Error) => console.error('Failed to load grid:', err));
  }, []);

  // Debounced route computation on cart changes
  const computeRoute = useCallback((items: CartItem[]) => {
    if (debounceRef.current) clearTimeout(debounceRef.current);

    if (items.length === 0) {
      setRoute(null);
      setRouteError(null);
      return;
    }

    debounceRef.current = setTimeout(() => {
      // Expand quantities: if quantity > 1, still send each product ID once
      // (route visits the location once regardless of quantity)
      const productIds = items.map((item) => item.product.id);
      setRouteLoading(true);
      setRouteError(null);

      calculateRoute(productIds)
        .then(setRoute)
        .catch((err: ApiError) => {
          setRouteError(err.message);
          setRoute(null);
        })
        .finally(() => setRouteLoading(false));
    }, 300);
  }, []);

  useEffect(() => {
    computeRoute(cartItems);
  }, [cartItems, computeRoute]);

  const handleAddToCart = useCallback((product: Product) => {
    setCartItems((prev) => {
      const existing = prev.find((item) => item.product.id === product.id);
      if (existing) {
        return prev.map((item) =>
          item.product.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item,
        );
      }
      return [...prev, { product, quantity: 1 }];
    });
  }, []);

  const handleUpdateQuantity = useCallback((productId: string, delta: number) => {
    setCartItems((prev) =>
      prev
        .map((item) =>
          item.product.id === productId
            ? { ...item, quantity: Math.max(0, item.quantity + delta) }
            : item,
        )
        .filter((item) => item.quantity > 0),
    );
  }, []);

  const handleRemove = useCallback((productId: string) => {
    setCartItems((prev) => prev.filter((item) => item.product.id !== productId));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-900">MallRobo</h1>
        <p className="text-sm text-gray-500">Mall Robot Shopping Cart System</p>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-6 grid grid-cols-1 lg:grid-cols-[250px_1fr_280px] gap-6">
        {/* Left panel: Store & Products */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-3">Store</h2>
            <StoreSelector
              onStoreSelect={setSelectedStoreId}
              selectedStoreId={selectedStoreId}
            />
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-3">Products</h2>
            <ProductList storeId={selectedStoreId} onAddToCart={handleAddToCart} />
          </div>
        </div>

        {/* Center panel: Grid Visualization + Route Stats */}
        <div className="space-y-4">
          <div className="bg-white rounded-lg shadow p-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-3">Robot Route</h2>
            <GridCanvas grid={grid} route={route} cartItems={cartItems} />
          </div>
          <RouteSummary route={route} loading={routeLoading} error={routeError} />
        </div>

        {/* Right panel: Cart */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-3">
              Cart ({cartItems.reduce((sum, i) => sum + i.quantity, 0)} items)
            </h2>
            <Cart
              items={cartItems}
              onUpdateQuantity={handleUpdateQuantity}
              onRemove={handleRemove}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
