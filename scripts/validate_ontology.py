import json
from pathlib import Path

path = Path("ontology/schemas/core.json")
data = json.loads(path.read_text())

required_nodes = {"project", "module", "agent", "workflow", "event", "repository"}

nodes = set(data.get("nodes", {}).keys())

missing = required_nodes - nodes

if missing:
    print("❌ Ontology invalid")
    print("Missing:", ", ".join(missing))
    exit(1)

print("✅ Ontology valid")
print(f"Nodes: {len(nodes)} | Edges: {len(data.get('edges', {}))}")
