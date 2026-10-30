"""Minimal interruptible animation controller with explicit transition policy."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Clip:
    name: str
    duration: float
    loop: bool
    def __post_init__(self):
        if self.duration <= 0: raise ValueError('positive clip duration required')

class AnimationController:
    def __init__(self, clips: dict[str,Clip]):
        if 'idle' not in clips: raise ValueError('idle clip required')
        self.clips=clips
        self.state='idle'
        self.time=0.0
        self.transitions=[]
    def request(self, state: str, allowed_from: set[str]):
        if state not in self.clips: raise KeyError(state)
        if self.state not in allowed_from: return False
        if self.state == state: return False
        self.transitions.append((self.state,state))
        self.state=state
        self.time=0.0
        return True
    def tick(self, dt: float):
        if dt < 0: raise ValueError('negative elapsed time')
        clip=self.clips[self.state]
        self.time+=dt
        if clip.loop: self.time %= clip.duration
        else: self.time = min(self.time,clip.duration)
        return self.time / clip.duration
