export interface Store {
  id: string;
  name: string;
}

export interface Product {
  id: string;
  name: string;
  price: number;
  x: number;
  y: number;
  store_id: string;
}

export interface Point {
  x: number;
  y: number;
}

export interface GridCell {
  x: number;
  y: number;
  path: boolean;
  robot_start: boolean;
}

export interface GridData {
  width: number;
  height: number;
  cells: GridCell[];
}

export interface RouteResponse {
  visit_order: Point[];
  cells: Point[];
  total_seconds: number;
  total_price: number;
  exact: boolean;
}

export interface CartItem {
  product: Product;
  quantity: number;
}
