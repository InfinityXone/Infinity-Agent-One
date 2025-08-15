
import psycopg2

def build_context_bundle(dsn: str, namespace: str, bias_ns: str = "origin", k: int = 6, bias_n: int = 4):
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT c.text FROM chunks c JOIN documents d ON d.id = c.document_id WHERE d.namespace = %s ORDER BY random() LIMIT %s", (namespace, k))
            ctx=[r[0] for r in cur.fetchall()]
            cur.execute("SELECT fragment FROM archetypes WHERE namespace=%s ORDER BY random() LIMIT %s", (bias_ns, bias_n))
            bias=[r[0] for r in cur.fetchall()]
    return {"context_chunks": ctx, "bias_fragments": bias}
