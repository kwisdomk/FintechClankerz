"use client";

import Link from "next/link";
import { useState } from "react";
import {
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  LayoutDashboard,
  List,
  ShieldCheck,
  UploadCloud,
} from "lucide-react";

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`flex shrink-0 flex-col bg-slate-900 text-slate-300 transition-[width] duration-200 ${
        collapsed ? "w-20" : "w-64"
      }`}
    >
      <div
        className={`flex min-h-16 items-center border-b border-slate-800 ${
          collapsed
            ? "flex-col justify-center gap-2 py-3"
            : "justify-between px-4"
        }`}
      >
        <div className="flex items-center">
          <ShieldCheck className="h-6 w-6 shrink-0 text-emerald-500" />
          {!collapsed && (
            <span className="ml-2 font-bold tracking-wide text-white">
              <span>FINTECH AI</span>
              <small className="ml-2 text-[10px] font-normal text-slate-400">Digital Surfers</small>
            </span>
          )}
        </div>
        <button
          type="button"
          onClick={() => setCollapsed((current) => !current)}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          aria-expanded={!collapsed}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          className="flex h-8 w-8 items-center justify-center rounded-md hover:bg-slate-800 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-emerald-500"
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </button>
      </div>
      <nav className="flex-1 space-y-2 px-3 py-6">
        <Link
          href="/dashboard"
          title={collapsed ? "Dashboard" : undefined}
          className={`flex items-center gap-3 rounded-md py-2 hover:bg-slate-800 hover:text-white transition-colors ${
            collapsed ? "justify-center px-2" : "px-3"
          }`}
        >
          <LayoutDashboard className="h-4 w-4 shrink-0" />
          {!collapsed && <span>Dashboard</span>}
        </Link>
        <Link
          href="/upload"
          title={collapsed ? "Import Data" : undefined}
          className={`flex items-center gap-3 rounded-md py-2 hover:bg-slate-800 hover:text-white transition-colors ${
            collapsed ? "justify-center px-2" : "px-3"
          }`}
        >
          <UploadCloud className="h-4 w-4 shrink-0" />
          {!collapsed && <span>Import Data</span>}
        </Link>
        <Link
          href="/transactions"
          title={collapsed ? "Transactions" : undefined}
          className={`flex items-center gap-3 rounded-md py-2 hover:bg-slate-800 hover:text-white transition-colors ${
            collapsed ? "justify-center px-2" : "px-3"
          }`}
        >
          <List className="h-4 w-4 shrink-0" />
          {!collapsed && <span>Transactions</span>}
        </Link>
        <Link
          href="/anomalies"
          title={collapsed ? "Anomalies & AI" : undefined}
          className={`flex items-center gap-3 rounded-md py-2 hover:bg-slate-800 hover:text-white transition-colors ${
            collapsed ? "justify-center px-2" : "px-3"
          }`}
        >
          <AlertTriangle className="h-4 w-4 shrink-0" />
          {!collapsed && <span>Anomalies &amp; AI</span>}
        </Link>
      </nav>
    </aside>
  );
}
