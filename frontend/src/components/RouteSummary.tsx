import type { RouteResponse } from '../types';

interface RouteSummaryProps {
  route: RouteResponse | null;
  loading: boolean;
  error: string | null;
}

export function RouteSummary({ route, loading, error }: RouteSummaryProps) {
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-3 text-red-700 text-sm">
        {error}
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-md p-3 text-gray-500 text-sm">
        Computing route...
      </div>
    );
  }

  if (!route) return null;

  return (
    <div className="grid grid-cols-3 gap-3">
     /* <div className="bg-white rounded-lg shadow p-4 flex flex-col items-center text-center">
        <span className="text-2xl mb-1" role="img" aria-label="Total price">
          💰
        </span>
        <span className="text-xs text-gray-500">Total Price</span>
        <span className="text-lg font-bold text-gray-900">
          ${Number(route.total_price).toFixed(2)}
        </span>
      </div>*/

      <div className="bg-white rounded-lg shadow p-4 flex flex-col items-center text-center">
        <span className="text-2xl mb-1" role="img" aria-label="Delivery time">
          ⏱️
        </span>
        <span className="text-xs text-gray-500">Delivery Time</span>
        <span className="text-lg font-bold text-gray-900">
          {route.total_seconds}s
        </span>
      </div>

      <div className="bg-white rounded-lg shadow p-4 flex flex-col items-center text-center">
        <span className="text-2xl mb-1" role="img" aria-label="Stops">
          📍
        </span>
        <span className="text-xs text-gray-500">Stops</span>
        <span className="text-lg font-bold text-gray-900">
          {route.visit_order.length}
        </span>
      </div>
    </div>
  );
}
