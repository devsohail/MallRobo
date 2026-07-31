import type { CartItem } from '../types';

interface CartProps {
  items: CartItem[];
  onUpdateQuantity: (productId: string, delta: number) => void;
  onRemove: (productId: string) => void;
}

export function Cart({ items, onUpdateQuantity, onRemove }: CartProps) {
  if (items.length === 0) {
    return <div className="text-gray-400 text-sm">Cart is empty</div>;
  }

  const totalPrice = items.reduce(
    (sum, item) => sum + Number(item.product.price) * item.quantity,
    0,
  );

  return (
    <div className="space-y-2">
      {items.map((item) => (
        <div
          key={item.product.id}
          className="flex items-center justify-between border border-gray-200 rounded-md p-2 bg-white"
        >
          <div className="flex-1">
            <div className="text-sm font-medium text-gray-900">{item.product.name}</div>
            <div className="text-xs text-gray-500">
              ${Number(item.product.price).toFixed(2)} each
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onUpdateQuantity(item.product.id, -1)}
              className="w-7 h-7 rounded bg-gray-200 text-gray-700 flex items-center justify-center hover:bg-gray-300"
            >
              -
            </button>
            <span className="text-sm font-medium w-6 text-center text-gray-900">{item.quantity}</span>
            <button
              onClick={() => onUpdateQuantity(item.product.id, 1)}
              className="w-7 h-7 rounded bg-gray-200 text-gray-700 flex items-center justify-center hover:bg-gray-300"
            >
              +
            </button>
            <button
              onClick={() => onRemove(item.product.id)}
              className="ml-2 text-red-500 hover:text-red-700 text-sm"
            >
              Remove
            </button>
          </div>
        </div>
      ))}
      <div className="text-right font-semibold text-gray-900 pt-2 border-t">
        Total: ${totalPrice.toFixed(2)}
      </div>
    </div>
  );
}
