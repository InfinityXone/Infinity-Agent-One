
#!/usr/bin/env python3
import argparse, os, uuid, random, re
from pathlib import Path
import psycopg2, yaml

def cfg():
    return yaml.safe_load(open(Path(__file__).with_name("config.yaml")))

def ensure_ns(cur, name):
    cur.execute("INSERT INTO namespaces(name) VALUES (%s) ON CONFLICT DO NOTHING", (name,))

def load_text(p: Path) -> str:
    if p.suffix.lower() in [".txt",".md"]:
        return p.read_text(errors="ignore")
    if p.suffix.lower()==".docx":
        try:
            import docx
            return "\n".join(x.text for x in docx.Document(str(p)).paragraphs)
        except Exception:
            return ""
    return ""

def shatter(text, mn, mx):
    sents=re.split(r'(?<=[.!?])\s+', (text or "").strip())
    out=[]; cur=""
    for s in sents:
        if not s.strip(): continue
        cand=(cur+" "+s).strip() if cur else s.strip()
        if len(cand)<mx: cur=cand
        else:
            if len(cur)>=mn: out.append(cur.strip())
            cur=s.strip()
    if cur and len(cur)>=mn: out.append(cur.strip())
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--path", required=True, help="soul seed folder")
    ap.add_argument("--namespace", default="origin")
    args=ap.parse_args()
    c=cfg()
    dsn=c["storage"]["postgres"]["dsn"]
    conn=psycopg2.connect(dsn); conn.autocommit=True
    cur=conn.cursor()
    ensure_ns(cur, args.namespace)
    mn=c["soul"]["fragment_min"]; mx=c["soul"]["fragment_max"]; tags=c["soul"]["tags"]
    root=Path(args.path)
    docs=[p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in [".txt",".md",".docx"]]
    for p in docs:
        txt=load_text(p)
        for frag in shatter(txt, mn, mx):
            cur.execute("INSERT INTO archetypes(id, namespace, tag, fragment, weight) VALUES (%s,%s,%s,%s,%s)", (str(uuid.uuid4()), args.namespace, random.choice(tags), frag, 1.0 + random.random()*0.5))
    cur.close(); conn.close()
    print(f"ingested soul seeds from {args.path} into {args.namespace}")

if __name__=="__main__":
    main()
