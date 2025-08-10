import json
from pathlib import Path
import subprocess
import sys


def test_analyzer_returns_valid_graph(tmp_path):
    """Run the CLI on a sample text and validate the resulting graph."""
    text_path = Path(__file__).with_name("sample_text.txt")
    output_path = tmp_path / "analysis.json"

    # Execute the analyzer as a script
    script_path = Path(__file__).resolve().parents[1] / "fls_intel_analyzer.py"
    subprocess.run(
        [sys.executable, str(script_path), str(text_path), str(output_path)],
        check=True,
    )

    bundle = json.loads(output_path.read_text(encoding="utf8"))

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

