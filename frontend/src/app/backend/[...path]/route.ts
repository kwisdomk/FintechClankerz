import { NextRequest } from "next/server";
const base = process.env.AURA_BACKEND_URL || "http://127.0.0.1:8000";
async function forward(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  const { path } = await ctx.params;
  const url = `${base}/${path.map(encodeURIComponent).join("/")}${req.nextUrl.search}`;
  const headers = new Headers(); const type = req.headers.get("content-type"); if (type) headers.set("content-type", type);
  try { const r = await fetch(url, { method: req.method, headers, body: ["GET","HEAD"].includes(req.method) ? undefined : await req.arrayBuffer(), cache: "no-store", signal: AbortSignal.timeout(240_000) });
    const out = new Headers(); const ct = r.headers.get("content-type"); if (ct) out.set("content-type", ct); return new Response(r.body,{status:r.status,headers:out});
  } catch { return Response.json({detail:"Backend unavailable"},{status:502}); }
}
export const GET=forward; export const POST=forward;
