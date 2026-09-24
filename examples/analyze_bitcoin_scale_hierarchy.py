"""Exploratory adjacent-scale extremum hierarchy on a single 15m price path.

Relationships are retrospective: a node at index i is confirmed at i+1, and
its parent can be confirmed still later. Never expose this graph as a live signal
before both endpoints have been confirmed.
"""
from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

from analyze_bitcoin_scale_trajectory import TAUS, block_null, ema, extrema, idx, load, near, tol


def link_levels(fine, coarse, tau):
    """Each fine extremum has at most one same-kind coarse parent.

    A coarse parent may have multiple fine children; an unmatched coarse node is
    a birth at this sampled scale. These are matching-dependent graph labels.
    """
    index = idx(coarse)
    children = Counter()
    matched = 0
    for pos, kind, _ in fine:
        parent = near(index, pos, kind, tol(tau))
        if parent is not None:
            children[(parent[0], parent[1])] += 1
            matched += 1
    births = sum((pos, kind) not in children for pos, kind, _ in coarse)
    merges = sum(count >= 2 for count in children.values())
    excess_children = sum(count - 1 for count in children.values())
    return {
        "fine": len(fine), "coarse": len(coarse),
        "matched_fine": matched, "unmatched_fine": len(fine)-matched,
        "coarse_births": births, "coarse_merges": merges,
        "excess_children": excess_children,
        "birth_rate": births/len(coarse) if coarse else None,
        "merge_rate": merges/len(coarse) if coarse else None,
    }


def hierarchy(prices):
    previous = extrema(ema(prices, TAUS[0]))
    out = []
    for tau in TAUS[1:]:
        current = extrema(ema(prices, tau))
        out.append({"from_tau": tau//2, "to_tau": tau,
                    **link_levels(previous, current, tau)})
        previous = current
    return out


def main():
    root = Path("data/bitcoin/coinbase")
    prices = [p for _, p in load(root/"btc_usd_15m.csv")]
    real = hierarchy(prices)
    # Prespecified sensitivity to local-dependence length; one realization per
    # block length is descriptive, not a permutation p-value.
    nulls = [{"block_bars": b, "links": hierarchy(block_null(prices, random.Random(20260924+b), b))}
             for b in (24, 96, 384)]
    output = {
        "method": "adjacent-scale nearest same-kind parent; 2*sqrt(tau) tolerance",
        "status": "RETROSPECTIVE",
        "confirmation": "an extremum at i is known at i+1; an edge only after both endpoints confirmed",
        "null_note": "one block-shuffled realization per block size; descriptive sensitivity only",
        "interpretation": "birth and merge are properties of this matching graph, not verified market events",
        "real": real, "block_nulls": nulls,
    }
    (root/"scale_space_hierarchy.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
