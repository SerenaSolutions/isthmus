# -*- coding: utf-8 -*-
"""Budget: contador de tiros e chamadas de oraculo. Recusa antes de estourar."""
from .errors import Refusal


class Budget:
    def __init__(self, shots, oracle_calls=1):
        self.shots_limit = int(shots)
        self.oracle_limit = int(oracle_calls)
        self.shots_used = 0
        self.oracle_used = 0

    def spend(self, shots=0, oracle=0):
        if self.shots_used + shots > self.shots_limit:
            raise Refusal("ISTH-BUDGET", f"tiros {self.shots_used}+{shots} > {self.shots_limit}")
        if self.oracle_used + oracle > self.oracle_limit:
            raise Refusal("ISTH-BUDGET", f"oraculo {self.oracle_used}+{oracle} > {self.oracle_limit}")
        self.shots_used += shots
        self.oracle_used += oracle
        return self.snapshot()

    def snapshot(self):
        return {"shots_used": self.shots_used, "shots_limit": self.shots_limit,
                "oracle_used": self.oracle_used, "oracle_limit": self.oracle_limit}
