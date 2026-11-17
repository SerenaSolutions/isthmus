# -*- coding: utf-8 -*-
"""Ponta quantica: Prepare, Evolve, Measure, Reset e Flow."""
from .errors import Refusal

OPS = ("prepare", "evolve", "measure", "reset")


class Flow:
    def __init__(self):
        self.steps = []

    def add(self, name, **kw):
        name = name.lower()
        if name not in OPS:
            raise Refusal("ISTH-FLOW", f"operacao desconhecida: {name}")
        self.steps.append((name, kw))
        return self

    def run(self):
        if not self.steps or self.steps[0][0] != "prepare":
            raise Refusal("ISTH-FLOW", "flow sem prepare inicial")
        for i, (name, _) in enumerate(self.steps):
            if name == "reset" and i + 1 < len(self.steps) and self.steps[i + 1][0] != "prepare":
                raise Refusal("ISTH-FLOW", "reset sem prepare seguinte")
        return {"steps": [s[0] for s in self.steps], "count": len(self.steps)}
