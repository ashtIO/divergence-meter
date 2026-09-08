"""D-Mail composer.

A D-Mail is a short message sent backward through time to alter the record.
Here it alters the record on the default branch. Register is keyed to the
hidden state, so a reader who plots message sentiment against the contribution
graph recovers the latent chain. Nobody will do this.
"""
from __future__ import annotations

import random

from divergence import ALPHA, BETA, DELTA

TYPES = ["feat", "fix", "chore", "refactor", "perf", "docs", "build", "ci"]

SCOPES = ["synergy", "bandwidth", "velocity", "alignment", "throughput", "cadence",
          "enablement", "governance", "ideation", "runway", "parks", "recreation"]

VERBS = ["operationalize", "socialize", "right-size", "double-click into", "circle back on",
         "unpack", "sunset", "harden", "ideate around", "level-set on", "de-risk",
         "workshop", "cascade", "productize"]

ADJECTIVES = ["cross-functional", "north-star", "best-in-class", "mission-critical",
              "frictionless", "holistic", "scalable", "outcome-oriented", "load-bearing",
              "stakeholder-adjacent", "waffle-adjacent"]

NOUNS = ["synergies", "learnings", "deliverables", "touchpoints", "paradigms", "verticals",
         "low-hanging fruit", "action items", "value levers", "core competencies",
         "binders", "swim lanes"]

TAILS = ["ahead of Q3 planning", "per stakeholder alignment", "to unblock downstream teams",
         "at the 30,000-foot level", "in advance of the readout", "pending legal review",
         "as a forcing function", "to close the loop", "before the Harvest Festival",
         "without looping in Eagleton"]

# Jerry's name is wrong in every quarterly deck. The generator honours this.
GERGICH = ["jerry", "garry", "larry", "terry", "barry"]

FIELD_FLAVOUR = {
    ALPHA: [
        "I am big enough to admit that I am often inspired by myself",
        "no ceilings on this deliverable",
        "we are going to build the best damn pipeline this department has seen",
        "ovaries before brovaries, shipping anyway",
    ],
    BETA: [
        "no material change to the operating picture",
        "carried forward from the previous readout",
        "tracking to plan, plan unchanged",
    ],
    DELTA: [
        "actively working to reduce this department's output",
        "any government program that works is an accident",
        "blocked pending a meeting about the meeting",
        "I regret to inform the committee that I remain unavailable",
    ],
}

# Low-probability. The graph is noise; these are the signal that it is a joke.
ARTIFACTS = [
    ("feat(sebastian): 5,000 candles in the wind", 0.010),
    ("chore(divergence): el psy kongroo", 0.010),
    ("feat(dunshire): add fourth cone, rebalance ledger phase", 0.008),
    ("fix(sern): suppress unauthorized observation of the lab", 0.008),
    ("docs(gadget): rename Phone Microwave (name subject to change)", 0.008),
    ("perf(waffles): reduce time-to-syrup by 40%", 0.006),
    ("refactor(720): dissolve Entertainment 720, retain vibes", 0.006),
    ("chore(sweetums): decline the sponsorship, again", 0.005),
    ("feat(steiner): retain memory across worldline transition", 0.004),
    ("fix(tuturu): restore lab member greeting", 0.004),
]


def compose(field: int, rng: random.Random) -> str:
    for text, probability in ARTIFACTS:
        if rng.random() < probability:
            return text

    scope = rng.choice(SCOPES)
    if scope in ("governance", "alignment") and rng.random() < 0.25:
        scope = rng.choice(GERGICH)

    subject = (f"{rng.choice(VERBS)} {rng.choice(ADJECTIVES)} "
               f"{rng.choice(NOUNS)} {rng.choice(TAILS)}")
    message = f"{rng.choice(TYPES)}({scope}): {subject}"

    if rng.random() < 0.18:
        message += f"\n\n{rng.choice(FIELD_FLAVOUR[field])}"
    if rng.random() < 0.05:
        message += " (name subject to change)"
    return message
