#!/usr/bin/env python3
"""Fuzzy Logic based intelligence analyzer.

This module performs a simple multi-stage analysis over an input text:
1. **Extraction of assertions** using spaCy (subject-verb-object with negation).
2. **Computation of ``A_init``**, the initial assumption set with unit weight.
3. **Detection of attacks** between assertions based on basic contradiction rules.
4. **FLS algorithm** to propagate the influence of attacks using a chosen t-norm.

The implementation respects the postulates BP (boundedness), UP (uniqueness of
assignments), SWP (support/weight propagation via t-norm) and SDP (strong
defense principle through complementary attack reduction).

A small CLI is provided for generating an ``analysis_bundle.json`` from a text
file.  The CLI exposes an option to select the t-norm used by the FLS algorithm
(``min``/``product``/``lukasiewicz``).
"""
from __future__ import annotations

import argparse
import json
from typing import Dict, List, Any

try:
    import spacy
except Exception as exc:  # pragma: no cover - handled at runtime
    raise RuntimeError(
        "spaCy is required for fls_intel_analyzer. Please install it before running."  # noqa: E501
    ) from exc

# ---------------------------------------------------------------------------
# Stage 1: Extraction of assertions
# ---------------------------------------------------------------------------

def _load_model() -> "spacy.language.Language":
    """Load the spaCy English model, downloading if necessary."""
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        import subprocess
        import sys

        subprocess.run(
            [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
            check=True,
        )
        return spacy.load("en_core_web_sm")

def extract_assertions(text: str) -> List[Dict[str, Any]]:
    """Extract basic assertions from ``text`` using spaCy.

    Each assertion is represented as a dictionary with ``subject``, ``verb``,
    ``object`` (may be ``None``) and ``negated`` flag.
    """
    nlp = _load_model()
    doc = nlp(text)
    assertions: List[Dict[str, Any]] = []
    for sent in doc.sents:
        subj = verb = obj = None
        neg = False
        for token in sent:
            if token.dep_ in {"nsubj", "nsubjpass"} and subj is None:
                subj = token.lemma_.lower()
            elif token.dep_ in {"dobj", "pobj"} and obj is None:
                obj = token.lemma_.lower()
            if token.pos_ == "VERB" and verb is None:
                verb = token.lemma_.lower()
                neg = any(child.dep_ == "neg" for child in token.children)
        if subj and verb:
            assertions.append(
                {
                    "subject": subj,
                    "verb": verb,
                    "object": obj,
                    "negated": neg,
                }
            )
    return assertions

# ---------------------------------------------------------------------------
# Stage 2: Computation of A_init
# ---------------------------------------------------------------------------

def compute_A_init(assertions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Generate the initial assumption set ``A_init``.

    Each assertion receives a unique identifier ``Ai`` (UP) and an initial
    weight of ``1.0`` bounded within ``[0,1]`` (BP).
    """
    a_init: Dict[str, Dict[str, Any]] = {}
    for idx, assertion in enumerate(assertions):
        key = f"A{idx}"
        a_init[key] = {"assertion": assertion, "weight": 1.0}
    return a_init

# ---------------------------------------------------------------------------
# Stage 3: Detection of attacks
# ---------------------------------------------------------------------------

def detect_attacks(a_init: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect attacks between assertions.

    A strong attack is registered when two assertions share subject and verb
    but differ in negation.  A weak attack occurs when the subject matches but
    the verb differs.  Each attack entry contains ``from``, ``to`` and
    ``strength`` in ``[0,1]`` (BP).
    """
    attacks: List[Dict[str, Any]] = []
    items = list(a_init.items())
    for i in range(len(items)):
        id_i, ai = items[i]
        for j in range(i + 1, len(items)):
            id_j, aj = items[j]
            a_i = ai["assertion"]
            a_j = aj["assertion"]
            if a_i["subject"] == a_j["subject"] and a_i["verb"] == a_j["verb"]:
                if a_i["negated"] != a_j["negated"]:
                    attacks.extend(
                        [
                            {"from": id_i, "to": id_j, "strength": 1.0},
                            {"from": id_j, "to": id_i, "strength": 1.0},
                        ]
                    )
            elif a_i["subject"] == a_j["subject"]:
                attacks.extend(
                    [
                        {"from": id_i, "to": id_j, "strength": 0.5},
                        {"from": id_j, "to": id_i, "strength": 0.5},
                    ]
                )
    return attacks

# ---------------------------------------------------------------------------
# Stage 4: FLS algorithm
# ---------------------------------------------------------------------------

def _t_norm(a: float, b: float, mode: str) -> float:
    """Return the t-norm of ``a`` and ``b`` based on ``mode`` (SWP)."""
    if mode == "product":
        return a * b
    if mode == "lukasiewicz":
        return max(0.0, a + b - 1.0)
    # default: minimum t-norm
    return min(a, b)

def fls_algorithm(a_init: Dict[str, Dict[str, Any]], attacks: List[Dict[str, Any]], mode: str) -> Dict[str, Dict[str, Any]]:
    """Apply a simple FLS algorithm producing final valuations.

    The algorithm iteratively weakens attacked assertions using the selected
    t-norm while ensuring results remain within ``[0,1]`` (BP) and that each
    assertion keeps a single valuation (UP).  Attack reduction is performed via
    ``1 - strength * attacker_value`` (SDP).
    """
    values = {k: v["weight"] for k, v in a_init.items()}
    changed = True
    while changed:
        changed = False
        for atk in attacks:
            src = atk["from"]
            dst = atk["to"]
            strength = atk["strength"]
            src_val = values[src]
            dst_val = values[dst]
            adjusted = _t_norm(dst_val, 1.0 - strength * src_val, mode)
            adjusted = max(0.0, min(1.0, adjusted))  # BP
            if abs(adjusted - dst_val) > 1e-6:
                values[dst] = adjusted
                changed = True
    for k in a_init:
        a_init[k]["final"] = values[k]
    return a_init

# ---------------------------------------------------------------------------
# Full analysis pipeline and CLI
# ---------------------------------------------------------------------------

def analyze_text(text: str, tnorm: str = "min") -> Dict[str, Any]:
    """Run the full pipeline on ``text`` using ``tnorm``."""
    assertions = extract_assertions(text)
    a_init = compute_A_init(assertions)
    attacks = detect_attacks(a_init)
    a_final = fls_algorithm(a_init, attacks, tnorm)
    return {
        "assertions": assertions,
        "A_init": a_init,
        "attacks": attacks,
        "A_final": a_final,
    }

def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="FLS intelligence analyzer")
    parser.add_argument("input", help="Path to text file to analyze")
    parser.add_argument("output", help="Path to output analysis_bundle.json")
    parser.add_argument(
        "--t-norm",
        choices=["min", "product", "lukasiewicz"],
        default="min",
        help="T-norm used for the FLS algorithm",
    )
    args = parser.parse_args()
    with open(args.input, "r", encoding="utf8") as f:
        text = f.read()
    bundle = analyze_text(text, tnorm=args.t_norm)
    with open(args.output, "w", encoding="utf8") as f:
        json.dump(bundle, f, indent=2)

if __name__ == "__main__":  # pragma: no cover
    main()
