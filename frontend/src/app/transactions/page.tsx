import { Card, Table, TableHeader, TableRow, TableHead, TableBody, TableCell, Badge, Button } from "@/components/ui"
import { Search, Filter } from "lucide-react"

const mockTransactions = [
  { id: '1', date: '28 Oct 2026', desc: 'Office supplies', supplier: 'ABC Supplies', amount: 45000, status: 'normal' },
  { id: '2', date: '29 Oct 2026', desc: 'Consulting fees', supplier: 'Tech Corp', amount: 185000, status: 'flagged' },
]

export default function TransactionsPage() {
  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-900">Transaction Registry</h1>
      
      <Card className="overflow-hidden">
        {/* Filters */}
        <div className="p-4 border-b bg-slate-50 flex gap-4 items-center">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search by supplier or description..." 
              className="w-full pl-9 pr-4 py-2 text-sm border rounded-md focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
          </div>
          <Button variant="outline" className="gap-2"><Filter className="w-4 h-4"/> Filter</Button>
        </div>

        {/* Table */}
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Supplier</TableHead>
              <TableHead className="text-right">Amount</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {mockTransactions.map((txn) => (
              <TableRow key={txn.id}>
                <TableCell className="text-slate-600">{txn.date}</TableCell>
                <TableCell className="font-medium">{txn.desc}</TableCell>
                <TableCell>{txn.supplier}</TableCell>
                <TableCell className="text-right font-medium">KSh {txn.amount.toLocaleString()}</TableCell>
                <TableCell>
                  <Badge variant={txn.status === 'flagged' ? 'destructive' : 'secondary'}>
                    {txn.status}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <Button variant="outline">View</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  )
}