const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

export interface Summary { transaction_count: number; total_amount: number; finding_count: number; open_finding_count: number }
export interface Transaction { id: number; date: string; description: string; amount: number; currency: string; supplier: string | null; reference: string | null }
export interface Finding { id: number; transaction_id: number; finding_type: string; severity: string; status: string; evidence: string[]; date: string; description: string; amount: number; currency: string; supplier: string | null; reference: string | null }

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try { response = await fetch(`${API_BASE}${path}`, { ...init, headers: { ...(init?.body instanceof FormData ? {} : { "Content-Type": "application/json" }), ...init?.headers }, cache: "no-store" }); }
  catch { throw new Error(`Cannot reach backend at ${API_BASE}. Start FastAPI and check NEXT_PUBLIC_API_BASE_URL.`); }
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || `Request failed (${response.status})`);
  return body as T;
}
