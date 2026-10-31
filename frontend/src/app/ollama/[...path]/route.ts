import { NextRequest } from "next/server";
const allowed = new Set(["api/tags", "api/version", "api/generate", "api/chat"]);
async function forward(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  const { path } = await ctx.params; const endpoint = path.join("/");
  if (!allowed.has(endpoint) || (req.method !== "GET" && !(req.method === "POST" && ["api/generate","api/chat"].includes(endpoint)))) return Response.json({detail:"Ollama endpoint not allowed"},{status:404});
  const url = `http://127.0.0.1:11434/${endpoint}${req.nextUrl.search}`; const headers = new Headers(); const type = req.headers.get("content-type"); if(type) headers.set("content-type",type);
  try { const r=await fetch(url,{method:req.method,headers,body:["GET","HEAD"].includes(req.method)?undefined:await req.arrayBuffer(),cache:"no-store",signal:AbortSignal.timeout(300_000)}); const out=new Headers();const ct=r.headers.get("content-type");if(ct)out.set("content-type",ct);return new Response(r.body,{status:r.status,headers:out}); }
  catch { return Response.json({error:"Local Ollama inference service unavailable"},{status:502}); }
}
export const GET=forward; export const POST=forward;
