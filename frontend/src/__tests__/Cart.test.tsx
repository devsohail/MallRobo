import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { Cart } from '../components/Cart';
import { makeCartItem, makeProduct } from '../test/helpers';

describe('Cart', () => {
  it('shows empty message when cart is empty', () => {
    render(<Cart items={[]} onUpdateQuantity={vi.fn()} onRemove={vi.fn()} />);
    expect(screen.getByText('Cart is empty')).toBeInTheDocument();
  });

  it('renders cart items with name and price', () => {
    const items = [makeCartItem({ product: makeProduct({ name: 'Apple', price: 1.5 }) })];
    render(<Cart items={items} onUpdateQuantity={vi.fn()} onRemove={vi.fn()} />);
    expect(screen.getByText('Apple')).toBeInTheDocument();
    expect(screen.getByText('$1.50 each')).toBeInTheDocument();
  });

  it('shows correct quantity', () => {
    const items = [makeCartItem({ quantity: 3 })];
    render(<Cart items={items} onUpdateQuantity={vi.fn()} onRemove={vi.fn()} />);
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('calls onUpdateQuantity with +1 when + clicked', async () => {
    const user = userEvent.setup();
    const onUpdate = vi.fn();
    const items = [makeCartItem()];
    render(<Cart items={items} onUpdateQuantity={onUpdate} onRemove={vi.fn()} />);
    await user.click(screen.getByText('+'));
    expect(onUpdate).toHaveBeenCalledWith('prod-1', 1);
  });

  it('calls onUpdateQuantity with -1 when - clicked', async () => {
    const user = userEvent.setup();
    const onUpdate = vi.fn();
    const items = [makeCartItem()];
    render(<Cart items={items} onUpdateQuantity={onUpdate} onRemove={vi.fn()} />);
    await user.click(screen.getByText('-'));
    expect(onUpdate).toHaveBeenCalledWith('prod-1', -1);
  });

  it('calls onRemove when Remove clicked', async () => {
    const user = userEvent.setup();
    const onRemove = vi.fn();
    const items = [makeCartItem()];
    render(<Cart items={items} onUpdateQuantity={vi.fn()} onRemove={onRemove} />);
    await user.click(screen.getByText('Remove'));
    expect(onRemove).toHaveBeenCalledWith('prod-1');
  });

  it('calculates total price correctly', () => {
    const items = [
      makeCartItem({ product: makeProduct({ id: 'p1', price: 2.0 }), quantity: 3 }),
      makeCartItem({ product: makeProduct({ id: 'p2', price: 1.5 }), quantity: 2 }),
    ];
    render(<Cart items={items} onUpdateQuantity={vi.fn()} onRemove={vi.fn()} />);
    // 2.0 * 3 + 1.5 * 2 = 9.00
    expect(screen.getByText('Total: $9.00')).toBeInTheDocument();
  });
});
