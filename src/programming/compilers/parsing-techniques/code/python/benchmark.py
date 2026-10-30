"""CSV raw timing harness; does not hardcode measured outcomes."""
import argparse,csv,platform,sys,time,random
from parsing_reference import cyk_recognize

# a^n b^n grammar in CNF: S -> A B | A C ; C -> S B ; A -> a ; B -> b
GRAMMAR={'S':(('A','B'),('A','C')),'C':(('S','B'),),'A':(('a',),),'B':(('b',),)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--sizes',default='2,4,8,16,32')
    ap.add_argument('--repeats',type=int,default=10)
    ap.add_argument('--seed',type=int,default=311)
    ap.add_argument('--output',default='-')
    a=ap.parse_args()
    if a.repeats < 1: ap.error('repeats must be positive')
    rng=random.Random(a.seed)
    sizes=[int(s) for s in a.sizes.split(',')]
    if any(n<=0 or n>128 for n in sizes): ap.error('size n must be 1..128')
    import contextlib
    with (open(a.output,'w',newline='') if a.output!='-' else contextlib.nullcontext(sys.stdout)) as f:
        w=csv.writer(f);w.writerow(('algorithm','n_pairs','n_tokens','trial','seed','elapsed_ns','correct','python','platform'))
        for n in sizes:
            tokens=['a']*n+['b']*n
            assert cyk_recognize(GRAMMAR,'S',tokens)
            for k in range(a.repeats):
                # Vary run ordering reproducibly; keep grammar and accepted language fixed.
                _=rng.random()
                begin=time.perf_counter_ns();ok=cyk_recognize(GRAMMAR,'S',tokens);duration=time.perf_counter_ns()-begin
                w.writerow(('CYK',n,len(tokens),k,a.seed,duration,int(ok),platform.python_version(),platform.platform()))

if __name__=='__main__':main()
