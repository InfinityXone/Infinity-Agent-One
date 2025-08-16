import { NextRequest, NextResponse } from 'next/server';
const BROKER_URL = process.env.BROKER_URL || 'http://127.0.0.1:8001';
const AGENT_ID = process.env.AGENT_ID || 'FinSynapse';
const HANDSHAKE_HEADER = process.env.HANDSHAKE_HEADER || 'NEO-PULSE';
const INFINITY_BROKER_SECRET = process.env.INFINITY_BROKER_SECRET || '';
export async function POST(req: NextRequest) {
  try {
    const body = await req.json().catch(() => ({}));
    const r = await fetch(`${BROKER_URL}/exec`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${INFINITY_BROKER_SECRET}`,
        'x-handshake': HANDSHAKE_HEADER,
        'Agent-ID': AGENT_ID,
        'X-AI-Role': 'api-ai'
      },
      body: JSON.stringify(body),
    });
    const data = await r.json().catch(async () => ({ error: await r.text() }));
    return NextResponse.json(data, { status: r.status });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'proxy_failed' }, { status: 500 });
  }
}
export const dynamic = 'force-dynamic';
