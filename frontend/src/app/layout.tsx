import "./globals.css"
import Sidebar from "@/components/sidebar"
import BackendStatus from "@/components/backend-status"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="flex min-h-screen bg-slate-50 text-slate-900 font-sans">
        
        <Sidebar />

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <header className="h-16 bg-white border-b flex items-center justify-between px-8">
            <div className="font-medium text-slate-700">Digital Surfers · Financial audit workspace</div>
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