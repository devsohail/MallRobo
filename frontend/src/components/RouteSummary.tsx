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
    <div className="bg-blue-50 border border-blue-200 rounded-md p-4 space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-600">Total Price</span>
        <span className="font-semibold text-gray-900">${Number(route.total_price).toFixed(2)}</span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-600">Delivery Time</span>
        <span className="font-semibold text-gray-900">{route.total_seconds}s</span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-600">Solution</span>
        <span
          className={`text-xs px-2 py-0.5 rounded-full font-medium ${
            route.exact
              ? 'bg-green-100 text-green-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}
        >
          {route.exact ? 'Exact' : 'Heuristic'}
        </span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-600">Stops</span>
        <span className="font-semibold text-gray-900">{route.visit_order.length}</span>
      </div>
    </div>
  );
}
