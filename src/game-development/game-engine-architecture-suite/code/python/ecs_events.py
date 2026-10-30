"""Generation IDs and queued, ordered gameplay messages; single-thread teaching prototype."""
from collections import deque
from dataclasses import dataclass
@dataclass(frozen=True)
class Entity:
    index: int
    generation: int
class World:
    def __init__(self):
        self.slots=[]
        self.events=deque()
    def spawn(self,value):
        for i,(gen,alive,_) in enumerate(self.slots):
            if not alive:
                self.slots[i]=(gen,True,value)
                return Entity(i,gen)
        self.slots.append((1,True,value))
        return Entity(len(self.slots)-1,1)
    def get(self,entity):
        if not 0<=entity.index<len(self.slots): return None
        gen,alive,value=self.slots[entity.index]
        return value if gen==entity.generation and alive else None
    def destroy(self,entity):
        if self.get(entity) is None: return False
        gen,_,value=self.slots[entity.index]
        self.slots[entity.index]=(gen+1,False,None)
        return True
    def emit(self,event): self.events.append(event)
    def drain(self,handler):
        # Snapshot lets events produced by handlers run in the next update, not recursively.
        pending=list(self.events)
        self.events.clear()
        for event in pending: handler(event)

if __name__ == '__main__':
    w=World(); old=w.spawn('first');w.destroy(old);new=w.spawn('second')
    assert w.get(old) is None and w.get(new)=='second'
    w.emit('on-spawn');w.drain(print)
