"""Deterministic timing, exposure sheets, and sample-space curves.

Educational reference for the Animation Timing documentation suite.
All display frame indices are zero-based; ranges use [start, end).
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable
import csv

@dataclass(frozen=True)
class FrameRate:
    numerator: int = 24
    denominator: int = 1
    def __post_init__(self):
        if self.numerator <= 0 or self.denominator <= 0:
            raise ValueError('rate numerator and denominator must be positive')
    @property
    def fps(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)
    def time_at(self, frame: int) -> Fraction:
        if frame < 0:
            raise ValueError('nonnegative display-frame index required')
        return Fraction(frame, 1) / self.fps
    def frame_count(self, seconds: Fraction) -> int:
        if seconds < 0:
            raise ValueError('duration cannot be negative')
        # nearest integer, ties upward (documented; unlike Python round)
        x = Fraction(seconds) * self.fps
        return (2 * x.numerator + x.denominator) // (2 * x.denominator)

@dataclass(frozen=True)
class Exposure:
    drawing: str
    start: int
    length: int
    def __post_init__(self):
        if not self.drawing or self.start < 0 or self.length <= 0:
            raise ValueError('invalid exposure')
    @property
    def end(self) -> int:
        return self.start + self.length

@dataclass(frozen=True)
class Cue:
    name: str
    start: int
    end: int
    def __post_init__(self):
        if not self.name or self.start < 0 or self.end <= self.start:
            raise ValueError('invalid cue')

@dataclass
class ExposureSheet:
    frame_count: int
    exposures: list[Exposure]
    cues: list[Cue]
    def validate(self):
        if self.frame_count < 0:
            raise ValueError('frame_count must be nonnegative')
        cursor = 0
        for exposure in sorted(self.exposures, key=lambda e: e.start):
            if exposure.start != cursor:
                raise ValueError('gap or overlap at frame %d' % cursor)
            cursor = exposure.end
        if cursor != self.frame_count:
            raise ValueError('exposures do not cover shot duration')
        for cue in self.cues:
            if cue.end > self.frame_count:
                raise ValueError('cue outside shot')
        return self
    def rows(self, rate: FrameRate):
        self.validate()
        cues_by_frame: dict[int, list[str]] = {}
        for cue in self.cues:
            cues_by_frame.setdefault(cue.start, []).append(cue.name)
        for ex in self.exposures:
            for k in range(ex.start, ex.end):
                yield dict(frame=k, time_seconds=str(rate.time_at(k)),
                           drawing=ex.drawing, exposure_start=ex.start,
                           exposure_length=ex.length,
                           cue=';'.join(cues_by_frame.get(k, [])))
    def write_csv(self, path: str, rate: FrameRate):
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer=csv.DictWriter(f, fieldnames=['frame','time_seconds',
                'drawing','exposure_start','exposure_length','cue'])
            writer.writeheader()
            writer.writerows(self.rows(rate))

def on_twos(display_frames: int) -> ExposureSheet:
    if display_frames < 0:
        raise ValueError('negative shot length')
    exposures=[]
    for k in range(0, display_frames, 2):
        exposures.append(Exposure(f'D{k//2:03}', k, min(2, display_frames-k)))
    return ExposureSheet(display_frames, exposures, [])

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def smoothstep(u: float) -> float:
    u = clamp01(u)
    return u*u*(3.0 - 2.0*u)

def sample_position(start: float, end: float, elapsed: float,
                    duration: float, easing=smoothstep) -> float:
    if duration <= 0:
        raise ValueError('duration must be positive')
    return start + (end-start)*easing(clamp01(elapsed/duration))

def contact_drift(world_positions: Iterable[tuple[float,float]]) -> float:
    poses=list(world_positions)
    if not poses:
        return 0.0
    from math import hypot
    x0,y0=poses[0]
    return max(hypot(x-x0,y-y0) for x,y in poses)
