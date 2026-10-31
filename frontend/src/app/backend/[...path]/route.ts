import { NextRequest } from "next/server";

const base = process.env.AURA_BACKEND_URL || "http://127.0.0.1:8000";

async function forward(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  const { path } = await ctx.params;
  const route = path.join("/");
  const url = `${base}/${path.map(encodeURIComponent).join("/")}${req.nextUrl.search}`;
  const headers = new Headers();
  const type = req.headers.get("content-type");
  if (type) headers.set("content-type", type);

  try {
    const response = await fetch(url, {
      method: req.method,
      headers,
      body: ["GET", "HEAD"].includes(req.method) ? undefined : await req.arrayBuffer(),
      cache: "no-store",
      signal: AbortSignal.timeout(240_000),
    });
    // FastAPI's docs are rooted at / on the backend. Preserve their schema and
    // Try-it-out URLs when presenting them through the /backend proxy prefix.
    if (response.ok && req.method === "GET" && route === "openapi.json") {
      const schema = await response.json();
      schema.servers = [{ url: "/backend" }];
      return Response.json(schema);
    }
    if (response.ok && req.method === "GET" && ["docs", "redoc"].includes(route)) {
      const html = (await response.text()).replaceAll("/openapi.json", "/backend/openapi.json");
      return new Response(html, { headers: { "content-type": "text/html; charset=utf-8" } });
    }
    const out = new Headers();
    const contentType = response.headers.get("content-type");
    if (contentType) out.set("content-type", contentType);
    return new Response(response.body, { status: response.status, headers: out });
  } catch {
    return Response.json({ detail: "Backend unavailable" }, { status: 502 });
  }
}

export const GET = forward;
export const POST = forward;
