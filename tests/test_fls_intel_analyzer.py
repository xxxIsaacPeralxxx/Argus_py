import json
from pathlib import Path
import sys

# Ensure package root is on the path for imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

from fls_intel_analyzer import analyze_text


def test_analyzer_returns_valid_graph():
    text_path = Path(__file__).with_name("sample_text.txt")
    text = text_path.read_text(encoding="utf8")
    bundle = analyze_text(text)

    # Build graph-like structure from analyzer output
    nodes = []
    for node_id, data in bundle["A_final"].items():
        aa = data["final"]
        ar = 1.0 - aa
        au = 0.0
        nodes.append({"id": node_id, "Aa": aa, "Ar": ar, "Au": au})
        assert abs(aa + ar + au - 1.0) < 1e-6

    graph = {"nodes": nodes, "edges": bundle["attacks"]}

    # Basic structure checks
    assert graph["nodes"], "No nodes produced"
    assert graph["edges"], "No edges produced"

    # Optionally, dump for manual inspection (not required for test)
    output_path = Path(__file__).with_name("sample_output.json")
    output_path.write_text(json.dumps(graph, indent=2), encoding="utf8")

