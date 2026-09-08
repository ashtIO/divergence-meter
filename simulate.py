"""Dry-run the worldline before committing anything to it.

Renders a year of sampled activity as a contribution graph, using GitHub's own
quartile bucketing, so the shading you see here is the shading you would get.
"""
from __future__ import annotations

import random
import sys
from collections import Counter

sys.path.insert(0, "src")

from divergence import EPOCH, FIELD_NAME, STEINS_GATE_THRESHOLD, run_chain
from dmail import compose

SHADES = [" ", "░", "▒", "▓", "█"]


def bucket(counts):
    """GitHub shades relative to your own distribution, not an absolute scale."""
    active = sorted(c for c in counts if c > 0)
    if not active:
        return lambda c: 0
    q = [active[int(len(active) * f)] for f in (0.25, 0.50, 0.75)]
    return lambda c: 0 if c == 0 else 1 + sum(c >= t for t in q)


def render(days):
    counts = [c for _, c, _, _, _ in days]
    level = bucket(counts)
    weeks = {}
    for day, count, *_ in days:
        weeks.setdefault(day.isocalendar()[:2], {})[day.weekday()] = count
    order = sorted(weeks)
    rows = []
    for weekday, label in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        cells = "".join(SHADES[level(weeks[w].get(weekday, 0))] for w in order)
        rows.append(f"  {label} {cells}")
    return "\n".join(rows)


def streaks(days):
    longest_on = longest_off = on = off = 0
    for _, count, *_ in days:
        on, off = (on + 1, 0) if count else (0, off + 1)
        longest_on, longest_off = max(longest_on, on), max(longest_off, off)
    return longest_on, longest_off


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1048596
    days = list(run_chain(EPOCH, 364, seed=seed))

    counts = [c for _, c, _, _, _ in days]
    fields = Counter(FIELD_NAME[f] for _, _, f, _, _ in days)
    active = sum(1 for c in counts if c)
    on, off = streaks(days)
    final_divergence = days[-1][3]

    print(f"\n  DIVERGENCE METER  {final_divergence:.6f}  "
          f"[{'Steins;Gate' if final_divergence >= STEINS_GATE_THRESHOLD else 'Beta'} attractor field]\n")
    print(render(days))
    print(f"\n  {sum(counts)} observations across {active}/{len(days)} days "
          f"({active / len(days):.0%} coverage)")
    print(f"  longest streak {on} days, longest gap {off} days, "
          f"busiest day {max(counts)}")
    print("  attractor field occupancy: " +
          ", ".join(f"{k} {v / len(days):.0%}" for k, v in fields.most_common()))

    print("\n  sample D-Mails")
    rng = random.Random(seed)
    for _, _, field, _, _ in random.Random(seed).sample(days, 8):
        print("    " + compose(field, rng).splitlines()[0])

    citations = [(d, c) for d, _, _, _, c in days if c]
    if citations:
        print("\n  convergence points")
        for day, citation in citations:
            print(f"    {day}  {citation}")
    print()


if __name__ == "__main__":
    main()
