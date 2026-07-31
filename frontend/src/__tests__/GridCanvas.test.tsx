import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { GridCanvas } from '../components/GridCanvas';
import { makeCartItem, makeGrid, makeProduct, makeRoute } from '../test/helpers';

describe('GridCanvas', () => {
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

  it('shows S at robot start', () => {
    const grid = makeGrid();
    render(<GridCanvas grid={grid} route={null} cartItems={[]} />);
    expect(screen.getByText('S')).toBeInTheDocument();
  });

  it('shows visit order numbers when route is present', () => {
    const grid = makeGrid();
    const route = makeRoute({
      visit_order: [{ x: 1, y: 0 }, { x: 2, y: 0 }],
      cells: [
        { x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 },
        { x: 1, y: 0 }, { x: 0, y: 0 },
      ],
    });
    render(<GridCanvas grid={grid} route={route} cartItems={[]} />);
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
    expect(screen.getByText('Start')).toBeInTheDocument();
    expect(screen.getByText('Obstacle')).toBeInTheDocument();
    expect(screen.getByText('Route')).toBeInTheDocument();
    expect(screen.getByText('Pickup')).toBeInTheDocument();
  });
});
