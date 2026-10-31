// app/dashboard/page.tsx
"use client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui"
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"
import { DollarSign, FileText, AlertTriangle } from "lucide-react"

const mockData = [
  { date: 'Oct 22', amount: 4000 },
  { date: 'Oct 24', amount: 8000 },
  { date: 'Oct 26', amount: 15000 },
  { date: 'Oct 28', amount: 22000 },
]

export default function DashboardPage() {
  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-900">Overview Dashboard</h1>
        <div className="text-sm font-medium text-slate-700 bg-white px-4 py-2 border border-slate-200 rounded-md shadow-sm">Date Range: Oct 2026</div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between !border-b-0 pb-2">
            <CardTitle className="text-sm text-slate-600">Total Expenditure</CardTitle>
            <DollarSign className="w-4 h-4 text-emerald-600" />
          </CardHeader>
          <CardContent><div className="text-3xl font-bold text-slate-900">KSh 4.2M</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between !border-b-0 pb-2">
            <CardTitle className="text-sm text-slate-600">Transactions</CardTitle>
            <FileText className="w-4 h-4 text-slate-400" />
          </CardHeader>
          <CardContent><div className="text-3xl font-bold text-slate-900">1,492</div></CardContent>
        </Card>
        <Card className="border-red-200 bg-red-50">
          <CardHeader className="flex flex-row items-center justify-between !border-b-0 pb-2">
            <CardTitle className="text-sm text-red-800">Duplicates</CardTitle>
            <AlertTriangle className="w-4 h-4 text-red-600" />
          </CardHeader>
          <CardContent><div className="text-3xl font-bold text-red-700">3</div></CardContent>
        </Card>
        <Card className="border-amber-200 bg-amber-50">
          <CardHeader className="flex flex-row items-center justify-between !border-b-0 pb-2">
            <CardTitle className="text-sm text-amber-800">Unusual Amounts</CardTitle>
            <AlertTriangle className="w-4 h-4 text-amber-600" />
          </CardHeader>
          <CardContent><div className="text-3xl font-bold text-amber-700">7</div></CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Spending Over Time</CardTitle></CardHeader>
        <CardContent className="h-[350px] pt-6">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={mockData}>
              <XAxis dataKey="date" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `KSh ${val/1000}k`} />
              <Tooltip cursor={{fill: '#f8fafc'}} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
              <Line type="monotone" dataKey="amount" stroke="#10b981" strokeWidth={3} dot={{r: 4, fill: '#10b981', strokeWidth: 2, stroke: '#fff'}} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}