import networkx as nx
from itertools import combinations
from app.vectorstore.seed_data import FRAUD_CASES

_graph = None


def build_pattern_graph() -> nx.Graph:
    """
    Builds a co-occurrence graph of fraud signals.
    Nodes = individual signals (e.g. 'new_device', 'money_mule_pattern')
    Edges = how often two signals appear together across historical cases,
            weighted by frequency and split by outcome (fraud vs false_positive).
    """
    g = nx.Graph()

    for case in FRAUD_CASES:
        signals = [s.strip() for s in case["pattern"].split("+")]
        outcome = case["outcome"]

        for signal in signals:
            if not g.has_node(signal):
                g.add_node(signal, fraud_count=0, false_positive_count=0)
            if outcome == "confirmed_fraud":
                g.nodes[signal]["fraud_count"] += 1
            else:
                g.nodes[signal]["false_positive_count"] += 1

        for sig_a, sig_b in combinations(signals, 2):
            if g.has_edge(sig_a, sig_b):
                g[sig_a][sig_b]["weight"] += 1
            else:
                g.add_edge(sig_a, sig_b, weight=1)

    return g


def get_pattern_graph() -> nx.Graph:
    global _graph
    if _graph is None:
        _graph = build_pattern_graph()
    return _graph


def get_related_patterns(signals: list, top_k: int = 5) -> list:
    """
    Given the signals detected on the current transaction, find related
    signals from the graph (things that historically co-occur with them)
    plus each signal's fraud-vs-false-positive track record.
    """
    g = get_pattern_graph()
    related_scores = {}

    for signal in signals:
        if not g.has_node(signal):
            continue
        for neighbor in g.neighbors(signal):
            if neighbor in signals:
                continue
            weight = g[signal][neighbor]["weight"]
            related_scores[neighbor] = related_scores.get(neighbor, 0) + weight

    top_related = sorted(related_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    results = []
    for pattern, co_occurrence_weight in top_related:
        node_data = g.nodes[pattern]
        fraud_count = node_data["fraud_count"]
        fp_count = node_data["false_positive_count"]
        total = fraud_count + fp_count
        fraud_rate = round(fraud_count / total, 2) if total else 0.0
        results.append({
            "related_pattern": pattern,
            "co_occurrence_strength": co_occurrence_weight,
            "historical_fraud_rate": fraud_rate,
        })

    return results


def get_signal_fraud_rate(signal: str) -> float:
    g = get_pattern_graph()
    if not g.has_node(signal):
        return None
    node_data = g.nodes[signal]
    total = node_data["fraud_count"] + node_data["false_positive_count"]
    return round(node_data["fraud_count"] / total, 2) if total else None