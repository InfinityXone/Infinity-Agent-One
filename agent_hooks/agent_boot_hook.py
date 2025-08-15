
import yaml
from pathlib import Path
from ingestion.connector_example import build_context_bundle

cfg = yaml.safe_load(open(Path(__file__).with_name("../ingestion/config.yaml")))
dsn = cfg["storage"]["postgres"]["dsn"]
bundle = build_context_bundle(dsn, "etherverse", "origin")
print("[AgentOne] Context bundle ready:", {k: len(v) for k,v in bundle.items()})
