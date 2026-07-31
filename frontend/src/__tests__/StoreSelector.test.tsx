import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { StoreSelector } from '../components/StoreSelector';
import * as client from '../api/client';
import { makeStore } from '../test/helpers';

vi.mock('../api/client');

describe('StoreSelector', () => {
  it('shows loading state initially', () => {
    vi.mocked(client.getStores).mockReturnValue(new Promise(() => {})); // never resolves
    render(<StoreSelector onStoreSelect={vi.fn()} selectedStoreId={null} />);
    expect(screen.getByText('Loading stores...')).toBeInTheDocument();
  });

  it('renders stores from API', async () => {
    const stores = [
      makeStore({ id: 's1', name: 'Store A' }),
      makeStore({ id: 's2', name: 'Store B' }),
    ];
    vi.mocked(client.getStores).mockResolvedValue(stores);
    render(<StoreSelector onStoreSelect={vi.fn()} selectedStoreId={null} />);

    await waitFor(() => {
      expect(screen.getByText('Store A')).toBeInTheDocument();
      expect(screen.getByText('Store B')).toBeInTheDocument();
    });
  });

  it('calls onStoreSelect when store is selected', async () => {
    const user = userEvent.setup();
    const stores = [makeStore({ id: 's1', name: 'Store A' })];
    vi.mocked(client.getStores).mockResolvedValue(stores);
    const onSelect = vi.fn();
    render(<StoreSelector onStoreSelect={onSelect} selectedStoreId={null} />);

    await waitFor(() => expect(screen.getByText('Store A')).toBeInTheDocument());
    await user.selectOptions(screen.getByRole('combobox'), 's1');
    expect(onSelect).toHaveBeenCalledWith('s1');
  });

  it('shows error when API fails', async () => {
    vi.mocked(client.getStores).mockRejectedValue(new Error('Network error'));
    render(<StoreSelector onStoreSelect={vi.fn()} selectedStoreId={null} />);

    await waitFor(() => {
      expect(screen.getByText('Error: Network error')).toBeInTheDocument();
    });
  });
});
