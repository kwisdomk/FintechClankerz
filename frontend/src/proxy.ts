import { NextRequest, NextResponse } from "next/server";

// Fail closed: never expose the demo tunnel without an explicit shared team secret.
export function proxy(request: NextRequest) {
  const password = process.env.TEAM_ACCESS_PASSWORD;
  if (!password) return new NextResponse("Team access is not configured.", { status: 503 });
  const expected = `Basic ${btoa(`team:${password}`)}`;
  if (request.headers.get("authorization") === expected) return NextResponse.next();
  return new NextResponse("Authentication required.", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="Fintech AI team demo", charset="UTF-8"' },
  });
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
