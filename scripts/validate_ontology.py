import json
from pathlib import Path

file = Path("ontology/schemas/core.json")

data = json.loads(file.read_text())

required_nodes = ["project", "module", "agent", "workflow", "event"]

missing = [n for n in required_nodes if n not in data.get("nodes", {})]

if missing:
    print("Ontology invalid. Missing nodes:", missing)
    exit(1)

print("Ontology valid ✓")
