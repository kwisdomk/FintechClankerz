"use client"
import { useState } from "react"
import { Card, CardContent, Button } from "@/components/ui"
import { UploadCloud, CheckCircle2 } from "lucide-react"

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile?.type === "text/csv") setFile(droppedFile)
  }

  return (
    <div className="max-w-3xl mx-auto mt-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Import Financial Data</h1>
        <p className="text-slate-500 mt-1">Upload supplier invoices and transaction records for AI auditing.</p>
      </div>
      
      <Card>
        <div 
          className="border-2 border-dashed border-slate-200 bg-slate-50 hover:bg-slate-100 transition-colors rounded-xl flex flex-col items-center justify-center py-20 m-6"
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
        >
          <UploadCloud className="w-12 h-12 text-slate-400 mb-4" />
          <p className="text-lg font-medium text-slate-800">Drop your CSV file here</p>
          <p className="text-sm text-slate-500 mb-6">Accepted formats: .csv only</p>
          <Button variant="outline">Browse Files</Button>
        </div>
      </Card>

      {file && (
        <Card className="border-emerald-200 bg-emerald-50 overflow-hidden">
          <div className="p-4 flex justify-between items-center">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-6 h-6 text-emerald-600" />
              <div>
                <p className="font-semibold text-emerald-900">{file.name}</p>
                <p className="text-sm text-emerald-700">{(file.size / 1024).toFixed(2)} KB · Ready to process</p>
              </div>
            </div>
            <Button>Run AI Audit</Button>
          </div>
        </Card>
      )}
    </div>
  )
}