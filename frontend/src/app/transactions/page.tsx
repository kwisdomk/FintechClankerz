"use client";
import { useEffect, useState } from "react";
import { Search } from "lucide-react";
import { Card, Table, TableHeader, TableRow, TableHead, TableBody, TableCell, Badge, Button } from "@/components/ui";
import { api, Transaction } from "@/lib/api";

type Page = { items: Transaction[]; total: number; limit: number; offset: number };
const pageSize = 50;

export default function TransactionsPage() {
  const [data, setData] = useState<Page | null>(null);
  const [request, setRequest] = useState({ query: "", offset: 0 });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const controller = new AbortController();
    const timer = setTimeout(() => {
      const params = new URLSearchParams({ limit: String(pageSize), offset: String(request.offset), q: request.query });
      api<Page>("/api/transactions?" + params, { signal: controller.signal })
        .then(result => { if (!controller.signal.aborted) { setData(result); setError(""); setLoading(false); } })
        .catch(cause => { if (!controller.signal.aborted) { setError(cause.message); setLoading(false); } });
    }, 200);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [request]);

  function navigate(offset: number, query = request.query) {
    setLoading(true);
    setRequest({ offset, query });
  }

  return <div className="mx-auto max-w-6xl space-y-6">
    <div><p className="text-sm font-semibold text-emerald-700">RECORDS</p><h1 className="text-3xl font-bold">Transaction registry</h1><p className="mt-1 text-slate-500">{data ? data.total + " matching records" : "Loading records…"}</p></div>
    {error && <p role="alert" className="rounded bg-amber-50 p-3 text-amber-900">{error} {data && "Previously loaded records are shown below."}</p>}
    <Card className="overflow-hidden">
      <div className="border-b bg-slate-50 p-4"><div className="relative max-w-lg">
        <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" aria-hidden="true" />
        <input aria-label="Search all transactions" value={request.query} onChange={event => navigate(0, event.target.value)} placeholder="Search supplier, description, reference…" className="w-full rounded-md border bg-white py-2 pl-9 pr-3 text-sm" />
      </div></div>
      <div className="overflow-x-auto" aria-busy={loading}><Table><TableHeader><TableRow><TableHead>Date</TableHead><TableHead>Description</TableHead><TableHead>Supplier</TableHead><TableHead className="text-right">Amount</TableHead><TableHead>Reference</TableHead></TableRow></TableHeader><TableBody>
        {data?.items.map(item => <TableRow key={item.id}><TableCell>{item.date}</TableCell><TableCell className="font-medium">{item.description}</TableCell><TableCell>{item.supplier || "—"}</TableCell><TableCell className="text-right whitespace-nowrap">{item.currency} {item.amount.toLocaleString()}</TableCell><TableCell><Badge variant="secondary">{item.reference || "—"}</Badge></TableCell></TableRow>)}
        {!data?.items.length && <TableRow><TableCell colSpan={5} className="py-10 text-center text-slate-500">{loading ? "Loading records…" : error ? "Records are unavailable." : request.query ? "No matching transactions." : "No transactions yet. Import a CSV to get started."}</TableCell></TableRow>}
      </TableBody></Table></div>
      <div className="flex flex-wrap items-center justify-between gap-3 border-t p-4 text-sm text-slate-600">
        <span aria-live="polite">{loading ? "Loading…" : data?.total ? (data.offset + 1) + "–" + (data.offset + data.items.length) + " of " + data.total : "0 records"}</span>
        <div className="flex gap-2"><Button variant="outline" disabled={loading || !data || data.offset === 0} onClick={() => navigate(Math.max(0, request.offset - pageSize))}>Previous</Button><Button variant="outline" disabled={loading || !data || data.offset + pageSize >= data.total} onClick={() => navigate(request.offset + pageSize)}>Next</Button></div>
      </div>
    </Card>
  </div>;
}
