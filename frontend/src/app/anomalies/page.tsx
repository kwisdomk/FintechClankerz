// app/anomalies/page.tsx
import { Card, CardHeader, CardTitle, CardContent, Badge, Button } from "@/components/ui"
import { Server, Cloud, BrainCircuit, Activity } from "lucide-react"

export default function AnomaliesPage() {
  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-900">Investigations & AI Explanations</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card className="border-slate-300">
            <CardHeader className="bg-white flex flex-row justify-between items-start">
              <div>
                <CardTitle className="text-xl flex items-center gap-3">
                  Transaction #TXN-1042
                  <Badge variant="destructive" className="uppercase tracking-wider">High Priority</Badge>
                </CardTitle>
                <p className="text-sm font-medium text-slate-600 mt-2">KSh 185,000 · ABC Office Supplies · 29 October 2026</p>
              </div>
              <Badge variant="secondary" className="bg-emerald-50 text-emerald-700 border-emerald-200">Investigation Open</Badge>
            </CardHeader>
            <CardContent className="space-y-6">
              
              <div>
                <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2 mb-3">
                  <BrainCircuit className="w-5 h-5 text-emerald-600" /> AI Finding: Why it was flagged
                </h4>
                <div className="text-sm text-slate-800 bg-slate-50 p-5 rounded-md border border-slate-200 leading-relaxed space-y-3">
                  <p>• The amount is significantly above the supplier's historical average of KSh 25,000.</p>
                  <p>• A similar payment was recorded three days earlier, indicating a potential duplicate.</p>
                  <p>• The payment reference format does not match standard internal structures.</p>
                </div>
              </div>

              <div>
                <h4 className="text-sm font-bold text-slate-900 mb-3">Observed Evidence</h4>
                <div className="space-y-3">
                  <div className="text-sm flex justify-between p-4 bg-white border border-slate-200 rounded-md shadow-sm">
                    <span className="font-medium text-slate-700">26 Oct - ABC Office Supplies (Previous)</span>
                    <span className="font-bold text-slate-900">KSh 185,000</span>
                  </div>
                  <div className="text-sm flex justify-between p-4 bg-red-50 border border-red-200 rounded-md shadow-sm">
                    <span className="font-medium text-red-900">29 Oct - ABC Office Supplies (Flagged)</span>
                    <span className="font-bold text-red-900">KSh 185,000</span>
                  </div>
                </div>
              </div>

              <div className="border-t border-slate-100 pt-6">
                <Button className="w-full">Chat with Gemma 4 about this finding</Button>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader className="bg-slate-50">
              <CardTitle className="text-sm flex items-center gap-2 text-slate-800">
                <Activity className="w-4 h-4 text-emerald-600" /> AI Infrastructure Status
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              
              <div className="flex items-center justify-between p-4 border border-slate-200 rounded-md bg-white shadow-sm">
                <div className="flex items-center gap-3">
                  <Server className="w-5 h-5 text-slate-500" />
                  <div>
                    <p className="text-sm font-bold text-slate-900">Local Inference</p>
                    <p className="text-xs text-slate-500 mt-0.5">Ollama · Gemma 4</p>
                  </div>
                </div>
                <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200">Connected</Badge>
              </div>

              <div className="flex items-center justify-between p-4 border border-slate-200 rounded-md bg-white shadow-sm">
                <div className="flex items-center gap-3">
                  <Cloud className="w-5 h-5 text-slate-500" />
                  <div>
                    <p className="text-sm font-bold text-slate-900">Cloud Inference</p>
                    <p className="text-xs text-slate-500 mt-0.5">Gemma 4 Provider</p>
                  </div>
                </div>
                <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200">Connected</Badge>
              </div>

              <div className="mt-6 pt-6 border-t border-slate-100 text-sm">
                <p className="font-bold text-slate-900 mb-4">Latest Inference Lifecycle</p>
                <div className="space-y-3">
                  <div className="flex justify-between items-center"><span className="text-slate-500">Model Used:</span> <span className="font-medium text-slate-900">Local Gemma 4</span></div>
                  <div className="flex justify-between items-center"><span className="text-slate-500">Execution:</span> <span className="font-medium text-slate-900">Local</span></div>
                  <div className="flex justify-between items-center"><span className="text-slate-500">Duration:</span> <span className="font-medium text-slate-900">2.4 seconds</span></div>
                  <div className="flex justify-between items-center"><span className="text-slate-500">Escalation:</span> <span className="font-medium text-slate-900">Not required</span></div>
                </div>
              </div>

            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}