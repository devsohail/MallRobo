import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { ProductList } from '../components/ProductList';
import * as client from '../api/client';
import { makeProduct } from '../test/helpers';

vi.mock('../api/client');

describe('ProductList', () => {
  it('shows placeholder when no store selected', () => {
    render(<ProductList storeId={null} onAddToCart={vi.fn()} />);
    expect(screen.getByText('Select a store to view products')).toBeInTheDocument();
  });

  it('shows loading state while fetching', () => {
    vi.mocked(client.getStoreProducts).mockReturnValue(new Promise(() => {}));
    render(<ProductList storeId="s1" onAddToCart={vi.fn()} />);
    expect(screen.getByText('Loading products...')).toBeInTheDocument();
  });

  it('renders products for selected store', async () => {
    const products = [
      makeProduct({ id: 'p1', name: 'Apple', price: 1.5 }),
      makeProduct({ id: 'p2', name: 'Banana', price: 2.0 }),
    ];
    vi.mocked(client.getStoreProducts).mockResolvedValue(products);
    render(<ProductList storeId="s1" onAddToCart={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('Apple')).toBeInTheDocument();
      expect(screen.getByText('Banana')).toBeInTheDocument();
    });
  });

  it('calls onAddToCart when Add is clicked', async () => {
    const user = userEvent.setup();
    const product = makeProduct({ id: 'p1', name: 'Apple' });
    vi.mocked(client.getStoreProducts).mockResolvedValue([product]);
    const onAdd = vi.fn();
    render(<ProductList storeId="s1" onAddToCart={onAdd} />);

    await waitFor(() => expect(screen.getByText('Apple')).toBeInTheDocument());
    await user.click(screen.getByText('Add'));
    expect(onAdd).toHaveBeenCalledWith(product);
  });

  it('shows error when API fails', async () => {
    vi.mocked(client.getStoreProducts).mockRejectedValue(new Error('Server error'));
    render(<ProductList storeId="s1" onAddToCart={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('Error: Server error')).toBeInTheDocument();
    });
  });

  it('shows empty state when no products found', async () => {
    vi.mocked(client.getStoreProducts).mockResolvedValue([]);
    render(<ProductList storeId="s1" onAddToCart={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('No products found')).toBeInTheDocument();
    });
  });
});
