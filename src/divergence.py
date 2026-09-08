"""Worldline divergence sampler.

Daily observation volume is a hidden Markov chain over attractor fields with
negative binomial emissions. Real commit counts are overdispersed; a Poisson
would produce a suspiciously even graph, which is the one outcome we cannot have.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from pathlib import Path

# Attractor fields in the Steins;Gate sense: a basin the worldline settles into
# and resists leaving. Self-transition dominates, which is what produces the
# streaks and dead weeks that make a contribution graph read as human.
ALPHA, BETA, DELTA = 0, 1, 2

FIELD_NAME = {ALPHA: "Alpha", BETA: "Beta", DELTA: "Delta"}

# Same three states, presented upward.
FIELD_POSTURE = {
    ALPHA: "Hypergrowth Operating Posture",
    BETA: "Steady-State Delivery Cadence",
    DELTA: "Awaiting Stakeholder Alignment",
}

TRANSITION = {
    ALPHA: {ALPHA: 0.70, BETA: 0.24, DELTA: 0.06},
    BETA:  {ALPHA: 0.08, BETA: 0.80, DELTA: 0.12},
    DELTA: {ALPHA: 0.03, BETA: 0.19, DELTA: 0.78},
}

# (mean, dispersion k). Variance = mean + mean^2 / k, so smaller k is burstier.
EMISSION = {ALPHA: (4.6, 2.2), BETA: (2.0, 1.5), DELTA: (0.10, 0.8)}

WEEKDAY_WEIGHT = [1.0, 1.05, 1.0, 1.0, 0.90, 0.38, 0.26]  # Mon..Sun

# A freak 30-commit day would blow out GitHub's quartile thresholds and wash
# every other day pale, so the upper tail is truncated rather than left free.
DAILY_CEILING = 14

STEINS_GATE_THRESHOLD = 1.048596

# The worldline has an origin. Everything after it is replayed from here.
EPOCH = date(2026, 9, 1)
SEED = 1048596

# (month, day) -> (forced field or None, multiplier, citation)
CONVERGENCE_POINTS = {
    (10, 13): (ALPHA, 1.8, "Treat Yo Self. Fiscal restraint suspended for one operating day."),
    (2, 14):  (ALPHA, 1.4, "Galentine's Day observance. Ovaries before brovaries."),
    (7, 28):  (None, 1.6, "Time Travel Symposium. Attractor field instability expected."),
    (1, 24):  (DELTA, 0.0, "Departmental shutdown. Swanson directive: reduce output."),
}


def _poisson(lam: float, rng: random.Random) -> int:
    if lam <= 0:
        return 0
    target, k, p = pow(2.718281828459045, -lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= target:
            return k
        k += 1


def _negative_binomial(mean: float, k: float, rng: random.Random) -> int:
    """Gamma-Poisson mixture. Stdlib only, so the Action needs no dependencies."""
    if mean <= 0:
        return 0
    return _poisson(rng.gammavariate(k, mean / k), rng)


@dataclass
class ReadingSteiner:
    """State retained across worldlines. Without it every run starts cold and the
    chain loses its autocorrelation, which is the whole point of the chain."""
    field: int = BETA
    divergence: float = 0.337187
    observed_total: int = 0
    last_observed: str = ""

    @classmethod
    def load(cls, path: Path) -> "ReadingSteiner":
        if path.exists():
            return cls(**json.loads(path.read_text()))
        return cls()

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2) + "\n")


def advance_field(field: int, rng: random.Random) -> int:
    r, cumulative = rng.random(), 0.0
    for nxt, p in TRANSITION[field].items():
        cumulative += p
        if r < cumulative:
            return nxt
    return field


def observe(day: date, field: int, rng: random.Random) -> tuple[int, int, str | None]:
    """Return (count, effective_field, citation) for one worldline-day."""
    citation = None
    multiplier = WEEKDAY_WEIGHT[day.weekday()]

    event = CONVERGENCE_POINTS.get((day.month, day.day))
    if event:
        forced, boost, citation = event
        if forced is not None:
            field = forced
        multiplier *= boost

    mean, k = EMISSION[field]
    count = _negative_binomial(mean * multiplier, k, rng)
    return min(count, DAILY_CEILING), field, citation


def drift(current: float, count: int, field: int, rng: random.Random) -> float:
    """Random walk on the divergence reading. Reports six decimals of nothing."""
    step = rng.gauss(0.0, 0.004) + (count - 2.0) * 0.0011
    if field == ALPHA:
        step += 0.0025
    return max(0.0, min(1.999999, current + step))


def run_chain(start: date, days: int, seed: int = SEED):
    """Forward simulation. Used by simulate.py; the live job advances one day."""
    rng = random.Random(seed)
    steiner = ReadingSteiner()
    for offset in range(days):
        day = start + timedelta(days=offset)
        steiner.field = advance_field(steiner.field, rng)
        count, effective, citation = observe(day, steiner.field, rng)
        steiner.divergence = drift(steiner.divergence, count, effective, rng)
        steiner.observed_total += count
        yield day, count, effective, steiner.divergence, citation
