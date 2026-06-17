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
  owner_user_id: string;
  is_active: boolean;
  notes?: string;
  created_at: string;
}

// ── Livestock / Batches ───────────────────────────────────────────────────────

export type Species = 'broiler' | 'layer' | 'cattle' | 'sheep' | 'goat';
export type PoultrySpecies = 'broiler' | 'layer';
export type BatchStatus = 'quarantine' | 'active' | 'closed';
export type BatchCloseReason = 'sale' | 'slaughter' | 'transfer' | 'disease' | 'other';

export interface Batch {
  id: string;
  farm_id: string;
  section_id: string;
  species: PoultrySpecies;
  status: BatchStatus;
  batch_code?: string;
  initial_count: number;
  current_count: number;
  placement_date: string;
  quarantine_end_date?: string;
  closed_at?: string;
  close_reason?: BatchCloseReason;
  supplier_name?: string;
  chick_price_per_head?: number;
  notes?: string;
  total_mortality: number;
  survival_rate: number;
  created_at: string;
  updated_at: string;
}

// ── Mortality ─────────────────────────────────────────────────────────────────

export interface MortalityRecord {
  id: string;
  batch_id: string;
  farm_id: string;
  quantity: number;
  cause_category?: string;
  cause_description?: string;
  disposal_method?: string;
  deceased_at: string;
}

export interface MortalitySummary {
  batch_id: string;
  total_deaths: number;
  initial_count: number;
  current_count: number;
  mortality_rate: number;
  cause_breakdown: Record<string, number>;
}

// ── Weight Sampling ───────────────────────────────────────────────────────────

export interface WeightSampling {
  id: string;
  batch_id: string;
  farm_id: string;
  sample_size: number;
  average_weight_kg: number;
  total_sample_weight_kg?: number;
  age_days?: number;
  measured_at: string;
  notes?: string;
}

export interface GrowthMetrics {
  batch_id: string;
  sampling_count: number;
  latest_avg_weight_kg?: number;
  age_days?: number;
  adg_kg?: number;
  total_feed_kg?: number;
  fcr?: number;
}

// ── Vaccination ───────────────────────────────────────────────────────────────

export type VaccinationStatus = 'planned' | 'completed' | 'skipped' | 'overdue';

export interface VaccinationRecord {
  id: string;
  batch_id: string;
  farm_id: string;
  schedule_id?: string;
  vaccine_name: string;
  status: VaccinationStatus;
  scheduled_at?: string;
  vaccinated_at?: string;
  quantity_used?: number;
  unit?: string;
  vaccine_inventory_item_id?: string;
  notes?: string;
}

export interface VaccinationSchedule {
  id: string;
  farm_id: string;
  species: string;
  vaccine_name: string;
  day_of_age: number;
  is_mandatory: boolean;
  notes?: string;
}

// ── Feed Consumption ──────────────────────────────────────────────────────────

export interface FeedRecord {
  id: string;
  batch_id: string;
  farm_id: string;
  feed_date: string;
  feed_type?: string;
  quantity_kg: number;
  water_liters?: number;
  age_days?: number;
  notes?: string;
}

export interface FeedSummary {
  batch_id: string;
  total_feed_kg: number;
  total_water_liters?: number;
  record_count: number;
  fcr?: number;
}

// ── Sales ─────────────────────────────────────────────────────────────────────

export type SalePaymentStatus = 'paid' | 'pending'

export interface SaleRecord {
  id: string
  batch_id: string
  farm_id: string
  customer_name: string
  customer_phone?: string
  head_count: number
  quantity_kg: number
  price_per_kg_uzs: number
  total_revenue_uzs: number
  payment_status: SalePaymentStatus
  sold_at: string
  notes?: string
  created_at: string
}

export interface BatchSalesSummary {
  batch_id: string
  total_revenue_uzs: number
  sale_count: number
}

export interface BatchProfit {
  batch_id: string
  total_revenue_uzs: number
  total_cost_uzs: number
  gross_profit_uzs: number
  profit_margin_pct: number
  sale_count: number
  expense_count: number
}

// ── Reports ───────────────────────────────────────────────────────────────────

export interface BatchReport {
  batch_id: string
  generated_at: string
  batch_code: string | null
  farm_id: string
  species: string
  initial_count: number
  current_count: number
  status: string
  placement_date: string
  age_days: number | null
  fcr: number | null
  adg_grams: number | null
  latest_avg_weight_kg: number | null
  total_feed_kg: number | null
  total_water_liters: number | null
  total_deaths: number | null
  mortality_rate_pct: number | null
  survival_rate_pct: number | null
  total_cost_uzs: number | null
  total_revenue_uzs: number | null
  gross_profit_uzs: number | null
  profit_margin_pct: number | null
  sale_count: number | null
  expense_count: number | null
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

// ── Expenses / Cost Tracking ──────────────────────────────────────────────────

export type ExpenseCategory = 'feed' | 'veterinary' | 'labor' | 'transport' | 'equipment' | 'utilities' | 'depreciation' | 'other'
export type BatchExpenseType = 'feed' | 'vaccine' | 'medicine' | 'chick' | 'other'

export interface Expense {
  id: string
  farm_id: string
  batch_id?: string
  category: ExpenseCategory
  expense_type?: BatchExpenseType
  description: string
  amount: number
  currency: string
  source_event_id?: string
  expense_date: string
  notes?: string
  created_at: string
}

export interface BatchCostSummary {
  batch_id: string
  total_uzs: number
  breakdown: Record<string, number>
  expense_count: number
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
