import { useEffect, useRef, useState } from 'react';
import type { CartItem, GridData, RouteResponse } from '../types';

interface GridCanvasProps {
  grid: GridData | null;
  route: RouteResponse | null;
  cartItems: CartItem[];
}

const CELL_SIZE = 48;
const ANIMATION_STEP_MS = 50;

export function GridCanvas({ grid, route, cartItems }: GridCanvasProps) {
  const [animatedIndex, setAnimatedIndex] = useState(-1);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    // Clean up any running animation
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }

    if (!route || route.cells.length === 0) {
      setAnimatedIndex(-1);
      return;
    }

    // Start animation from index 0
    setAnimatedIndex(0);
    let current = 0;

    function tick() {
      current++;
      if (current < route!.cells.length) {
        setAnimatedIndex(current);
        timerRef.current = setTimeout(tick, ANIMATION_STEP_MS);
      } else {
        timerRef.current = null;
      }
    }

    timerRef.current = setTimeout(tick, ANIMATION_STEP_MS);

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [route]);

  if (!grid) return <div className="text-gray-500">Loading grid...</div>;

  const cellMap = new Map<string, { path: boolean; robot_start: boolean }>();
  for (const cell of grid.cells) {
    cellMap.set(`${cell.x},${cell.y}`, { path: cell.path, robot_start: cell.robot_start });
  }

  // Build route step map: "x,y" -> step number (first occurrence)
  const routeStepMap = new Map<string, number>();
  if (route) {
    for (let i = 0; i < route.cells.length; i++) {
      const key = `${route.cells[i].x},${route.cells[i].y}`;
      if (!routeStepMap.has(key)) {
        routeStepMap.set(key, i);
      }
    }
  }

  // Build animated route cell set (only cells up to animatedIndex)
  const animatedRouteCellSet = new Set<string>();
  const animationComplete = route ? animatedIndex >= route.cells.length - 1 : false;
  if (route && animatedIndex >= 0) {
    for (let i = 0; i <= Math.min(animatedIndex, route.cells.length - 1); i++) {
      animatedRouteCellSet.add(`${route.cells[i].x},${route.cells[i].y}`);
    }
  }

  // The current animation head cell
  const headKey =
    route && animatedIndex >= 0 && animatedIndex < route.cells.length
      ? `${route.cells[animatedIndex].x},${route.cells[animatedIndex].y}`
      : null;

  // Build product location map
  const productLocationMap = new Map<string, string[]>();
  for (const item of cartItems) {
    const key = `${item.product.x},${item.product.y}`;
    const names = productLocationMap.get(key) ?? [];
    names.push(item.product.name);
    productLocationMap.set(key, names);
  }

  // Build visit order markers
  const visitOrderMap = new Map<string, number>();
  if (route) {
    for (let i = 0; i < route.visit_order.length; i++) {
      const pt = route.visit_order[i];
      visitOrderMap.set(`${pt.x},${pt.y}`, i + 1);
    }
  }

  return (
    <div className="overflow-auto">
      <div
        className="inline-grid gap-0 border border-gray-300"
        style={{
          gridTemplateColumns: `repeat(${grid.width}, ${CELL_SIZE}px)`,
        }}
      >
        {Array.from({ length: grid.height }, (_, y) =>
          Array.from({ length: grid.width }, (_, x) => {
            const key = `${x},${y}`;
            const cell = cellMap.get(key);
            const isPath = cell?.path ?? false;
            const isStart = cell?.robot_start ?? false;
            const isRouteCell = animatedRouteCellSet.has(key);
            const visitNum = visitOrderMap.get(key);
            // Only show visit number if the animation has reached that cell
            const showVisitNum =
              visitNum !== undefined && isRouteCell && (animationComplete || animatedRouteCellSet.has(key));
            const isHead = !animationComplete && key === headKey;
            const productNames = productLocationMap.get(key);

            let bgColor = 'bg-gray-800'; // obstacle
            if (isPath) bgColor = 'bg-gray-100';
            if (isRouteCell) bgColor = 'bg-blue-200';
            if (isStart) bgColor = 'bg-green-400';
            if (showVisitNum) bgColor = 'bg-orange-400';

            const ringClass = isHead ? 'ring-2 ring-blue-500' : '';

            return (
              <div
                key={key}
                className={`${bgColor} ${ringClass} border border-gray-300 flex flex-col items-center justify-center text-xs relative`}
                style={{ width: CELL_SIZE, height: CELL_SIZE }}
                title={buildTooltip(x, y, isStart, productNames)}
              >
                {isStart && !showVisitNum && (
                  <span className="text-2xl" role="img" aria-label="Robot">🤖</span>
                )}
                {showVisitNum && (
                  <span className="text-white font-bold text-sm">{visitNum}</span>
                )}
                {productNames && !showVisitNum && !isStart && (
                  <span className="text-blue-800 font-bold">P</span>
                )}
              </div>
            );
          }),
        )}
      </div>
      <div className="mt-2 flex gap-4 text-xs text-gray-600">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-green-400 inline-block rounded" /> 🤖 Start
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-gray-800 inline-block rounded" /> Obstacle
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-blue-200 inline-block rounded" /> Route
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-orange-400 inline-block rounded" /> Pickup
        </span>
      </div>
    </div>
  );
}

function buildTooltip(
  x: number,
  y: number,
  isStart: boolean,
  productNames: string[] | undefined,
): string {
  let tip = `(${x}, ${y})`;
  if (isStart) tip += ' - Robot Start';
  if (productNames) tip += ` - ${productNames.join(', ')}`;
  return tip;
}
