"""Fixed-time-step replay, expressed in integer microseconds for repeatability."""
from dataclasses import dataclass
STEP_US = 10_000
@dataclass
class State:
    pos: float = 0.0
    velocity: float = 3.0
    ticks: int = 0

def simulate(frame_us, max_ticks_per_frame=None):
    state, accumulator, discarded = State(), 0, 0
    for delta in frame_us:
        if delta < 0:
            raise ValueError("negative frame duration")
        accumulator += delta
        steps = 0
        while accumulator >= STEP_US and (max_ticks_per_frame is None or steps < max_ticks_per_frame):
            state.pos += state.velocity * (STEP_US / 1_000_000)
            state.ticks += 1
            steps += 1
            accumulator -= STEP_US
        if max_ticks_per_frame is not None and accumulator >= STEP_US:
            skipped = accumulator // STEP_US
            discarded += skipped
            accumulator -= skipped * STEP_US
    return state, discarded, accumulator / STEP_US

if __name__ == '__main__':
    a = simulate([10_000] * 100)
    b = simulate([20_000] * 50)
    assert a[0].ticks == b[0].ticks == 100
    assert abs(a[0].pos - b[0].pos) < 1e-12
    print(f'ticks={a[0].ticks} position={a[0].pos:.6f}')
