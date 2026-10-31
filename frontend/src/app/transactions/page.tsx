"use client";
import { useEffect, useMemo, useState } from "react";
import { Search } from "lucide-react";
import { Card, Table, TableHeader, TableRow, TableHead, TableBody, TableCell, Badge } from "@/components/ui";
import { api, Transaction } from "@/lib/api";

export default function TransactionsPage() {
  const [items,setItems]=useState<Transaction[]>([]); const [query,setQuery]=useState(""); const [error,setError]=useState("");
  useEffect(()=>{ api<{items:Transaction[]}>('/api/transactions').then(x=>setItems(x.items)).catch(e=>setError(e.message)); },[]);
  const filtered=useMemo(()=>items.filter(t=>`${t.description} ${t.supplier||''} ${t.reference||''}`.toLowerCase().includes(query.toLowerCase())),[items,query]);
  return <div className="mx-auto max-w-6xl space-y-6"><div><p className="text-sm font-semibold text-emerald-700">RECORDS</p><h1 className="text-3xl font-bold">Transaction registry</h1><p className="mt-1 text-slate-500">{items.length} recent records</p></div>{error&&<p role="alert" className="rounded bg-amber-50 p-3 text-amber-900">{error}</p>}<Card className="overflow-hidden"><div className="border-b bg-slate-50 p-4"><div className="relative max-w-lg"><Search className="absolute left-3 top-3 h-4 w-4 text-slate-400"/><input aria-label="Search transactions" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search supplier, description, reference…" className="w-full rounded-md border bg-white py-2 pl-9 pr-3 text-sm"/></div></div><div className="overflow-x-auto"><Table><TableHeader><TableRow><TableHead>Date</TableHead><TableHead>Description</TableHead><TableHead>Supplier</TableHead><TableHead className="text-right">Amount</TableHead><TableHead>Reference</TableHead></TableRow></TableHeader><TableBody>{filtered.map(t=><TableRow key={t.id}><TableCell>{t.date}</TableCell><TableCell className="font-medium">{t.description}</TableCell><TableCell>{t.supplier||"—"}</TableCell><TableCell className="text-right">{t.currency} {t.amount.toLocaleString()}</TableCell><TableCell><Badge variant="secondary">{t.reference||"—"}</Badge></TableCell></TableRow>)}{!filtered.length&&<TableRow><TableCell colSpan={5} className="py-10 text-center text-slate-500">{items.length?"No matching transactions.":"No transactions yet. Import a CSV to get started."}</TableCell></TableRow>}</TableBody></Table></div></Card></div>;
}
