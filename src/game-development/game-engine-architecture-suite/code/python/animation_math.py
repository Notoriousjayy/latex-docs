"""Quaternion shortest-arc spherical interpolation, normalized outputs."""
from math import acos, cos, sin, sqrt

def normalize(q):
    n = sqrt(sum(a*a for a in q))
    if n <= 1e-15:
        raise ValueError("zero quaternion")
    return tuple(a/n for a in q)

def slerp(a, b, t):
    if not 0 <= t <= 1:
        raise ValueError("t must be in [0,1]")
    a, b = normalize(a), normalize(b)
    dot = sum(x*y for x,y in zip(a,b))
    if dot < 0.0:
        b = tuple(-v for v in b)
        dot = -dot
    dot = min(1.0, max(-1.0, dot))
    if dot > 0.9995:
        return normalize(tuple((1-t)*x+t*y for x,y in zip(a,b)))
    theta = acos(dot)
    s = sin(theta)
    return normalize(tuple((sin((1-t)*theta)*x+sin(t*theta)*y)/s for x,y in zip(a,b)))

if __name__ == '__main__':
    print(slerp((1,0,0,0),(0,0,0,1),0.5))
