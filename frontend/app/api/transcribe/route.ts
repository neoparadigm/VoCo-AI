import { NextRequest } from 'next/server'

const BACKEND = process.env.BACKEND_URL || 'http://localhost:8001'

export async function POST(request: NextRequest) {
  const body = await request.json()
  const res = await fetch(`${BACKEND}/transcribe`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await res.json()
  return Response.json(data, { status: res.status })
}
