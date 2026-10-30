"""One-dimensional bouncing rigid body's vertical coordinate (meters)."""
from dataclasses import dataclass
@dataclass
class Body:
    y: float = 4.0
    vy: float = 0.0

def tick(body, dt, gravity=-9.81, restitution=0.75):
    if not (0 < dt <= 1.0) or not (0 <= restitution <= 1):
        raise ValueError('invalid step or restitution')
    body.vy += gravity*dt
    body.y += body.vy*dt
    if body.y < 0.0:
        body.y = 0.0
        body.vy = max(0.0,-body.vy*restitution)
    return body

if __name__ == '__main__':
    b=Body()
    for _ in range(500): tick(b,0.01)
    print(f'y={b.y:.4f} vy={b.vy:.4f}')
