/**
 * AgroVision — Shared TypeScript type definitions.
 * These mirror the API contract from shared/contracts/api_standards.py.
 */

// ── API Response contracts ────────────────────────────────────────────────────

export interface APIResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: PaginationMeta;
  message?: string;
}

export interface ErrorResponse {
  success: false;
  error_code: string;
  message: string;
  details?: unknown;
  trace_id?: string;
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  roles: string[];
  farm_id?: string;
  is_active: boolean;
}

// ── Farm ──────────────────────────────────────────────────────────────────────

export type FarmType = 'poultry' | 'livestock' | 'dairy' | 'mixed';

export interface Farm {
  id: string;
  name: string;
  farm_type: FarmType;
  address?: string;
  region?: string;
  is_active: boolean;
  created_at: string;
}

// ── Livestock / Batches ───────────────────────────────────────────────────────

export type Species = 'broiler' | 'layer' | 'cattle' | 'sheep' | 'goat';
export type BatchStatus = 'quarantine' | 'active' | 'closed';

export interface Batch {
  id: string;
  farm_id: string;
  section_id: string;
  species: Species;
  status: BatchStatus;
  initial_count: number;
  current_count: number;
  placement_date: string;
  closed_at?: string;
  closing_reason?: string;
}

// ── Inventory ─────────────────────────────────────────────────────────────────

export type ItemType = 'feed' | 'vaccine' | 'medicine' | 'equipment' | 'packaging' | 'other';

export interface StockItem {
  id: string;
  warehouse_id: string;
  name: string;
  item_type: ItemType;
  unit: string;
  current_quantity: number;
  minimum_quantity: number;
  is_below_minimum: boolean;
}

// ── Finance ───────────────────────────────────────────────────────────────────

export type PaymentStatus = 'pending' | 'partial' | 'paid' | 'overdue' | 'written_off';

export interface SalesOrder {
  id: string;
  farm_id: string;
  customer_id: string;
  status: PaymentStatus;
  total_amount: number;
  paid_amount: number;
  outstanding_amount: number;
  currency: string;
  order_date: string;
  due_date?: string;
}

// ── Notifications ─────────────────────────────────────────────────────────────

export type NotificationSeverity = 'info' | 'warning' | 'critical';

export interface Notification {
  id: string;
  title: string;
  body: string;
  severity: NotificationSeverity;
  is_read: boolean;
  is_delivered: boolean;
  created_at: string;
}

// ── WebSocket ─────────────────────────────────────────────────────────────────

export interface WSMessage {
  type: 'notification' | 'kpi_update' | 'alert';
  payload: unknown;
}
