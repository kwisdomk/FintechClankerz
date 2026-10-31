"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
export default function BackendStatus(){const [online,setOnline]=useState<boolean|null>(null);useEffect(()=>{const check=()=>api('/api/health').then(()=>setOnline(true)).catch(()=>setOnline(false));void check();const id=setInterval(check,30000);return()=>clearInterval(id)},[]);return <span className="flex items-center gap-2 text-sm text-slate-600"><span className={`h-2 w-2 rounded-full ${online?'bg-emerald-500':online===false?'bg-red-500':'bg-amber-400'}`}/>{online?'Backend connected':online===false?'Backend offline':'Checking backend…'}</span>}
