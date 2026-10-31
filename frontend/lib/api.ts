// Use same-origin /api routes; Next route handlers proxy to the loopback-only backend.
const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL || "").replace(/\/$/, "");

export interface Summary { transaction_count: number; total_amount: number; finding_count: number; open_finding_count: number; totals_by_currency?: { currency: string; total_amount: number; transaction_count: number }[] }
export interface Transaction { id: number; date: string; description: string; amount: number; currency: string; supplier: string | null; reference: string | null }
export interface Finding { id: number; transaction_id: number; finding_type: string; severity: string; status: string; evidence: string[]; date: string; description: string; amount: number; currency: string; supplier: string | null; reference: string | null }

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try { response = await fetch(`${API_BASE}${path}`, { ...init, headers: { ...(init?.body instanceof FormData ? {} : { "Content-Type": "application/json" }), ...init?.headers }, cache: "no-store" }); }
  catch { throw new Error(`Cannot reach the API. Ensure the frontend proxy and local FastAPI backend are running.`); }
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = body.detail;
    const message = typeof detail === "string" ? detail
      : Array.isArray(detail) ? detail.map((item: { msg?: string }) => item.msg || "Invalid input").join("; ")
      : detail && typeof detail === "object" ? [detail.message, ...(detail.errors || [])].filter(Boolean).join(". ")
      : `Request failed (${response.status})`;
    throw new Error(message);
  }
  return body as T;
}
