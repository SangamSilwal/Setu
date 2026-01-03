import { type NextRequest, NextResponse } from "next/server"

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()

    const backendRes = await fetch("http://localhost:8000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })

    const data = await backendRes.json().catch(() => null)

    return NextResponse.json(data ?? { message: "No JSON response from backend" }, { status: backendRes.status })
  } catch (error) {
    console.error("/api/login proxy error:", error)
    return NextResponse.json({ error: "Proxy failed" }, { status: 500 })
  }
}
