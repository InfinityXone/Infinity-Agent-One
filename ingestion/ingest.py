
#!/usr/bin/env python3
import argparse, uuid
from pathlib import Path
import psycopg2, yaml

def read_cfg():
    return yaml.safe_load(open(Path(__file__).with_name("config.yaml")))

def ensure_ns(cur, name):
    cur.execute("INSERT INTO namespaces(name) VALUES (%s) ON CONFLICT DO NOTHING", (name,))

def upsert_doc(cur, ns, path: Path, title: str):
    import hashlib
    did = str(uuid.uuid4())
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    cur.execute(
        "INSERT INTO documents(id, namespace, source_uri, mime_type, title, sha256) VALUES (%s,%s,%s,%s,%s,%s)",
        (did, ns, str(path), "", title, sha)
    )
    return did

def chunk_text(txt, size=1000, overlap=150):
    txt = (txt or "").strip()
    if not txt:
        return []
    chunks = []
    i = 0
    while i < len(txt):
        chunk = txt[i:i+size]
        chunks.append(chunk)
        i += max(1, size - overlap)
    return chunks

def read_text(path: Path) -> str:
    if path.suffix.lower() in [".txt", ".md"]:
        return path.read_text(errors="ignore")
    if path.suffix.lower() == ".docx":
        try:
            import docx
            return "\n".join(p.text for p in docx.Document(str(path)).paragraphs)
        except Exception:
            return ""
    return ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True)
    ap.add_argument("--namespace", default=None)
    args = ap.parse_args()
    cfg = read_cfg()
    ns = args.namespace or cfg["ingest"]["default_namespace"]
    dsn = cfg["storage"]["postgres"]["dsn"]
    conn = psycopg2.connect(dsn); conn.autocommit = True
    cur = conn.cursor()
    ensure_ns(cur, ns)
    root = Path(args.path)
    docs = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in cfg["ingest"]["allowed_ext"]]
    for p in docs:
        did = upsert_doc(cur, ns, p, p.stem)
        chunks = chunk_text(read_text(p), cfg["ingest"]["chunk_size"], cfg["ingest"]["chunk_overlap"])
        for i, t in enumerate(chunks):
            import uuid as _u
            cid = str(_u.uuid4())
            cur.execute("INSERT INTO chunks(id, document_id, seq, text) VALUES (%s,%s,%s,%s)", (cid, did, i, t))
    cur.close(); conn.close()

if __name__ == "__main__":
    main()
