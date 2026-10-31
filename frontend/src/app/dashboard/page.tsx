"use client";
import { useEffect, useState } from "react";
import { AlertTriangle, FileText, Wallet, RefreshCw } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui";
import { api, Summary } from "@/lib/api";

export default function DashboardPage() {
  const [data, setData] = useState<Summary | null>(null);
  const [error, setError] = useState("");
  const load = () => api<Summary>("/api/summary").then(setData).catch(e => setError(e.message));
  useEffect(() => { void load(); }, []);
  const metrics = [
    { label: "Transactions", value: data?.transaction_count ?? "—", icon: FileText },
    { label: "Total transaction value", value: data ? `${data.total_amount.toLocaleString()}` : "—", icon: Wallet },
    { label: "Findings", value: data?.finding_count ?? "—", icon: AlertTriangle },
    { label: "Open for review", value: data?.open_finding_count ?? "—", icon: RefreshCw },
  ];
  return <div className="mx-auto max-w-6xl space-y-6">
    <div className="flex flex-wrap items-end justify-between gap-3"><div><p className="text-sm font-semibold text-emerald-700">DIGITAL SURFERS · FINTECH AI</p><h1 className="mt-1 text-3xl font-bold text-slate-900">Audit overview</h1><p className="mt-1 text-slate-500">Live metrics from your imported records.</p></div><button onClick={load} className="rounded-lg border bg-white px-4 py-2 text-sm hover:bg-slate-50">Refresh</button></div>
    {error && <div role="alert" className="rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">{error}</div>}
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{metrics.map(({label,value,icon:Icon})=><Card key={label}><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm text-slate-600">{label}</CardTitle><Icon className="h-4 w-4 text-emerald-600"/></CardHeader><CardContent><div className="text-3xl font-bold text-slate-900">{value}</div></CardContent></Card>)}</div>
    <Card><CardHeader><CardTitle>Review workflow</CardTitle></CardHeader><CardContent className="text-sm leading-6 text-slate-600">Import a transaction CSV, inspect rule-based duplicate findings, then request a Gemma explanation when useful. Findings come from deterministic checks; AI is optional and does not make audit decisions.</CardContent></Card>
  </div>;
}
