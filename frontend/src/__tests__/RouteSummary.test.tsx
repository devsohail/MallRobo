import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { RouteSummary } from '../components/RouteSummary';
import { makeRoute } from '../test/helpers';

describe('RouteSummary', () => {
  it('renders nothing when no route, not loading, no error', () => {
    const { container } = render(
      <RouteSummary route={null} loading={false} error={null} />,
    );
    expect(container.firstChild).toBeNull();
  });

  it('shows loading state', () => {
    render(<RouteSummary route={null} loading={true} error={null} />);
    expect(screen.getByText('Computing route...')).toBeInTheDocument();
  });

  it('shows error state', () => {
    render(<RouteSummary route={null} loading={false} error="Products unreachable" />);
    expect(screen.getByText('Products unreachable')).toBeInTheDocument();
  });

  it('displays correct total price', () => {
    const route = makeRoute({ total_price: 6.75 });
    render(<RouteSummary route={route} loading={false} error={null} />);
    expect(screen.getByText('$6.75')).toBeInTheDocument();
  });

  it('displays delivery time', () => {
    const route = makeRoute({ total_seconds: 12 });
    render(<RouteSummary route={route} loading={false} error={null} />);
    expect(screen.getByText('12s')).toBeInTheDocument();
  });

  it('displays number of stops', () => {
    const route = makeRoute({
      visit_order: [{ x: 1, y: 0 }, { x: 2, y: 0 }, { x: 3, y: 0 }],
    });
    render(<RouteSummary route={route} loading={false} error={null} />);
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('renders stat card icons', () => {
    const route = makeRoute();
    render(<RouteSummary route={route} loading={false} error={null} />);
    expect(screen.getByLabelText('Total price')).toBeInTheDocument();
    expect(screen.getByLabelText('Delivery time')).toBeInTheDocument();
    expect(screen.getByLabelText('Stops')).toBeInTheDocument();
  });

  it('error takes priority over loading', () => {
    render(<RouteSummary route={null} loading={true} error="Error occurred" />);
    expect(screen.getByText('Error occurred')).toBeInTheDocument();
    expect(screen.queryByText('Computing route...')).not.toBeInTheDocument();
  });
});
