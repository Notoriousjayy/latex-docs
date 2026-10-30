"""Small fixed-step motion simulator with explicit coordinate conventions."""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite

@dataclass
class Body:
    position: float
    velocity: float
    mass: float = 1.0
    def __post_init__(self):
        if not all(isfinite(x) for x in (self.position,self.velocity,self.mass)) or self.mass <= 0:
            raise ValueError('invalid physical state')
    def advance(self, dt: float, force: float):
        if dt <= 0 or not isfinite(dt) or not isfinite(force):
            raise ValueError('invalid step')
        self.velocity += force / self.mass * dt
        self.position += self.velocity * dt

@dataclass
class Spring:
    position: float
    velocity: float
    target: float
    omega: float = 7.0
    zeta: float = 0.7
    def step(self, dt: float):
        if not 0 < dt <= 0.02 or self.omega <= 0 or self.zeta < 0:
            raise ValueError('unstable or nonphysical spring settings')
        accel=-2*self.zeta*self.omega*self.velocity - self.omega**2*(self.position-self.target)
        self.velocity += accel*dt
        self.position += self.velocity*dt
        return self.position

class FixedStepAccumulator:
    def __init__(self, step_seconds=1/120, max_steps=8):
        if step_seconds <= 0 or max_steps < 1:
            raise ValueError('bad fixed-step settings')
        self.h=step_seconds
        self.accumulator=0.0
        self.max_steps=max_steps
    def advance(self, wall_dt: float, callback):
        if wall_dt < 0 or not isfinite(wall_dt):
            raise ValueError('bad wall delta')
        self.accumulator+=wall_dt
        steps=0
        while self.accumulator + 1e-12 >= self.h and steps < self.max_steps:
            callback(self.h)
            self.accumulator-=self.h
            steps+=1
        # The caller owns overload policy. Residual is retained, not silently dropped.
        return steps, min(1.0, self.accumulator/self.h)
