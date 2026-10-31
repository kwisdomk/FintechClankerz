import "./globals.css"
import Sidebar from "@/components/sidebar"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="flex h-screen bg-slate-50 text-slate-900 font-sans">
        
        <Sidebar />

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <header className="h-16 bg-white border-b flex items-center justify-between px-8">
            <div className="font-medium text-slate-700">Workspace: Demo Business</div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
              <span className="text-sm text-slate-500">AI System Active</span>
            </div>
          </header>
          <main className="flex-1 overflow-y-auto p-8">
            {children}
          </main>
        </div>

      </body>
    </html>
  )
}