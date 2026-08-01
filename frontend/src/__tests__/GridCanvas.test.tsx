import { act, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { GridCanvas } from '../components/GridCanvas';
import { makeCartItem, makeGrid, makeProduct, makeRoute } from '../test/helpers';

describe('GridCanvas', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('shows loading when grid is null', () => {
    render(<GridCanvas grid={null} route={null} cartItems={[]} />);
    expect(screen.getByText('Loading grid...')).toBeInTheDocument();
  });

  it('renders grid cells', () => {
    const grid = makeGrid();
    const { container } = render(
      <GridCanvas grid={grid} route={null} cartItems={[]} />,
    );
    // 3x3 grid = 9 cells
    const cells = container.querySelectorAll('[title]');
    expect(cells.length).toBe(9);
  });

  it('shows robot emoji at robot start', () => {
    const grid = makeGrid();
    render(<GridCanvas grid={grid} route={null} cartItems={[]} />);
    expect(screen.getByLabelText('Robot')).toBeInTheDocument();
  });

  it('shows visit order numbers when route animation completes', () => {
    const grid = makeGrid();
    const route = makeRoute({
      visit_order: [{ x: 1, y: 0 }, { x: 2, y: 0 }],
      cells: [
        { x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 },
        { x: 1, y: 0 }, { x: 0, y: 0 },
      ],
    });
    render(<GridCanvas grid={grid} route={route} cartItems={[]} />);

    // Fast-forward animation: 5 cells * 50ms = 250ms
    act(() => {
      vi.advanceTimersByTime(250);
    });

    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('shows P for product locations not in visit order', () => {
    const grid = makeGrid();
    const cartItems = [
      makeCartItem({ product: makeProduct({ x: 1, y: 1, name: 'Widget' }) }),
    ];
    render(<GridCanvas grid={grid} route={null} cartItems={cartItems} />);
    expect(screen.getByText('P')).toBeInTheDocument();
  });

  it('renders legend items', () => {
    const grid = makeGrid();
    render(<GridCanvas grid={grid} route={null} cartItems={[]} />);
    expect(screen.getByText('Obstacle')).toBeInTheDocument();
    expect(screen.getByText('Route')).toBeInTheDocument();
    expect(screen.getByText('Pickup')).toBeInTheDocument();
  });

  it('animates route cells sequentially', () => {
    const grid = makeGrid();
    const route = makeRoute({
      visit_order: [{ x: 1, y: 0 }],
      cells: [
        { x: 0, y: 0 }, { x: 1, y: 0 }, { x: 0, y: 0 },
      ],
    });
    const { container } = render(<GridCanvas grid={grid} route={route} cartItems={[]} />);

    // At t=0, only first cell (0,0) should be in route (animatedIndex=0)
    // The cell at (1,0) should not yet have the route highlight
    const cellAt1_0 = container.querySelector('[title="(1, 0)"]');
    expect(cellAt1_0?.className).not.toContain('bg-blue-200');

    // Advance by 50ms — animatedIndex becomes 1, cell (1,0) should be highlighted
    act(() => {
      vi.advanceTimersByTime(50);
    });
    expect(cellAt1_0?.className).toContain('bg-orange-400');
  });
});
