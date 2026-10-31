import type { Metadata } from "next";
import "./globals.css"
import Sidebar from "@/components/sidebar"
import BackendStatus from "@/components/backend-status"

export const metadata: Metadata = { title: "FinGuard AI", description: "Import transactions, inspect possible duplicates, and record human review decisions." };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="app-shell flex min-h-screen bg-slate-50 text-slate-900 font-sans">
        
        <Sidebar />

        {/* Main Content */}
        <div className="min-w-0 flex-1 flex flex-col overflow-hidden">
          <header className="h-16 bg-white border-b flex items-center justify-between px-8">
            <div className="font-medium text-slate-700">FinGuard AI · Digital Surfers</div>
            <BackendStatus />
          </header>
          <main className="flex-1 overflow-y-auto p-4 sm:p-8">
            {children}
          </main>
        </div>

      </body>
    </html>
  )
}