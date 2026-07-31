import { useEffect, useState } from 'react';
import { getStoreProducts } from '../api/client';
import type { Product } from '../types';

interface ProductListProps {
  storeId: string | null;
  onAddToCart: (product: Product) => void;
}

export function ProductList({ storeId, onAddToCart }: ProductListProps) {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!storeId) {
      setProducts([]);
      return;
    }
    setLoading(true);
    setError(null);
    getStoreProducts(storeId)
      .then(setProducts)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [storeId]);

  if (!storeId) return <div className="text-gray-400 text-sm">Select a store to view products</div>;
  if (loading) return <div className="text-gray-500">Loading products...</div>;
  if (error) return <div className="text-red-500">Error: {error}</div>;
  if (products.length === 0) return <div className="text-gray-400 text-sm">No products found</div>;

  return (
    <div className="space-y-2">
      {products.map((product) => (
        <div
          key={product.id}
          className="flex items-center justify-between border border-gray-200 rounded-md p-3 bg-white"
        >
          <div>
            <div className="font-medium text-gray-900">{product.name}</div>
            <div className="text-sm text-gray-500">
              ${Number(product.price).toFixed(2)} &middot; ({product.x}, {product.y})
            </div>
          </div>
          <button
            onClick={() => onAddToCart(product)}
            className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-colors"
          >
            Add
          </button>
        </div>
      ))}
    </div>
  );
}
