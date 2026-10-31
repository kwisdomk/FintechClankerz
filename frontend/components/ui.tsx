// components/ui.tsx
import * as React from "react"

export function Card({ className, children }: { className?: string, children: React.ReactNode }) {
  return <div className={`rounded-xl border border-slate-200 bg-white text-slate-900 shadow-sm overflow-hidden ${className || ''}`}>{children}</div>
}
export function CardHeader({ className, children }: { className?: string, children: React.ReactNode }) {
  return <div className={`flex flex-col space-y-1.5 p-6 border-b border-slate-100 ${className || ''}`}>{children}</div>
}
export function CardTitle({ className, children }: { className?: string, children: React.ReactNode }) {
  return <h3 className={`font-semibold leading-none tracking-tight text-slate-900 ${className || ''}`}>{children}</h3>
}
export function CardContent({ className, children }: { className?: string, children: React.ReactNode }) {
  return <div className={`p-6 pt-4 ${className || ''}`}>{children}</div>
}

export function Button({ className, children, variant = 'primary', ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'outline' }) {
  const base = "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 h-9 px-4 py-2"
  const variants = {
    primary: "bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm",
    outline: "border border-slate-300 bg-white hover:bg-slate-50 text-slate-900"
  }
  return <button className={`${base} ${variants[variant]} ${className || ''}`} {...props}>{children}</button>
}

export function Badge({ className, variant = 'default', children }: { className?: string, variant?: 'default' | 'destructive' | 'secondary', children: React.ReactNode }) {
  const variants = {
    default: "bg-slate-900 text-white",
    secondary: "bg-slate-100 text-slate-700 border border-slate-200",
    destructive: "bg-red-100 text-red-700 border border-red-200"
  }
  return <div className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${variants[variant]} ${className || ''}`}>{children}</div>
}

export const Table = ({ children }: { children: React.ReactNode }) => <div className="relative w-full overflow-auto bg-white"><table className="w-full caption-bottom text-sm">{children}</table></div>
export const TableHeader = ({ children }: { children: React.ReactNode }) => <thead className="bg-slate-50 border-b border-slate-200">{children}</thead>
export const TableBody = ({ children }: { children: React.ReactNode }) => <tbody className="[&_tr:last-child]:border-0">{children}</tbody>
export const TableRow = ({ children }: { children: React.ReactNode }) => <tr className="border-b border-slate-200 transition-colors hover:bg-slate-50">{children}</tr>
export const TableHead = ({ children, className }: { children: React.ReactNode, className?: string }) => <th className={`h-10 px-4 text-left align-middle font-semibold text-slate-700 ${className || ''}`}>{children}</th>
export const TableCell = ({ children, className, colSpan }: { children: React.ReactNode, className?: string, colSpan?: number }) => <td colSpan={colSpan} className={`p-4 align-middle text-slate-700 ${className || ''}`}>{children}</td>