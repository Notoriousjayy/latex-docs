"""Example: python benchmark.py --max-power 13 --repeats 15 --batch 20 --csv results.csv

Measured output is written only when run; no benchmark data are fabricated.
"""
import argparse, csv, platform, random, statistics, time, sys
from algorithms import Record, stable_merge_sort, insertion_sort

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--max-power',type=int,default=12)
    parser.add_argument('--repeats',type=int,default=15)
    parser.add_argument('--batch',type=int,default=10)
    parser.add_argument('--csv',default='results.csv')
    args=parser.parse_args()
    if args.max_power<5 or args.repeats<1 or args.batch<1: parser.error('invalid sizes')
    rng=random.Random(42)
    rows=[]
    for power in range(5,args.max_power+1):
        n=2**power
        data=[Record(rng.randrange(n//2+1),i) for i in range(n)]
        expected=sorted(data,key=lambda r:r.key)
        for variant,method in [('insertion', insertion_sort),('merge', stable_merge_sort)]:
            if method(data)!=expected:raise AssertionError('wrong output')
            method(data) # warmup
            for run in range(args.repeats):
                begin=time.perf_counter_ns();check=0
                for _ in range(args.batch):
                    out=method(data);check^=out[-1].key if out else 0
                elapsed=time.perf_counter_ns()-begin
                rows.append(dict(language='python',version=platform.python_version(),variant=variant,
                                 n=n,input_family='uniform-key-fixed-seed',seed=42,run=run,
                                 batch_ops=args.batch,elapsed_ns=elapsed,checksum=check))
    with open(args.csv,'w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print('python',sys.version.split()[0], 'rows',len(rows),'written to',args.csv)
    for size in sorted(set(int(row['n']) for row in rows)):
        for variant in ('insertion','merge'):
            samples=[r['elapsed_ns']/r['batch_ops'] for r in rows if r['n']==size and r['variant']==variant]
            print(size,variant,'median ns/op',round(statistics.median(samples)))
if __name__=='__main__': main()
