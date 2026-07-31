import { useEffect, useState } from 'react';
import { getStores } from '../api/client';
import type { Store } from '../types';

interface StoreSelectorProps {
  onStoreSelect: (storeId: string) => void;
  selectedStoreId: string | null;
}

export function StoreSelector({ onStoreSelect, selectedStoreId }: StoreSelectorProps) {
  const [stores, setStores] = useState<Store[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getStores()
      .then(setStores)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-gray-500">Loading stores...</div>;
  if (error) return <div className="text-red-500">Error: {error}</div>;

  return (
    <div>
      <label htmlFor="store-select" className="block text-sm font-medium text-gray-700 mb-1">
        Select Store
      </label>
      <select
        id="store-select"
        value={selectedStoreId ?? ''}
        onChange={(e) => onStoreSelect(e.target.value)}
        className="w-full border border-gray-300 rounded-md px-3 py-2 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">-- Choose a store --</option>
        {stores.map((store) => (
          <option key={store.id} value={store.id}>
            {store.name}
          </option>
        ))}
      </select>
    </div>
  );
}
