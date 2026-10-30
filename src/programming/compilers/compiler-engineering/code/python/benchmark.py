"""Record measured batch execution times; no prepopulated benchmark results."""
import argparse,csv,statistics,time
from parser import parse,eval_ast
from optimizer import fold

p=argparse.ArgumentParser()
p.add_argument('--repeats',type=int,default=15)
p.add_argument('--batch',type=int,default=3000)
p.add_argument('--csv',default='benchmark-results.csv')
a=p.parse_args()
if a.repeats<5 or a.batch<1: p.error('repeats >=5 and batch >=1 required')
expr='(41 + 1) * (7-3) + 2'
a0=parse(expr);a1=fold(a0)
assert eval_ast(a0)==eval_ast(a1)
for tree in (a0,a1):
    for _ in range(100):eval_ast(tree)
rows=[]
for i in range(a.repeats):
    for name,tree in ((('baseline',a0),('folded',a1)) if i%2==0 else (('folded',a1),('baseline',a0))):
        t=time.perf_counter_ns()
        for _ in range(a.batch):eval_ast(tree)
        rows.append({'iteration':i,'variant':name,'batch':a.batch,'elapsed_ns':time.perf_counter_ns()-t})
with open(a.csv,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['iteration','variant','batch','elapsed_ns']);w.writeheader();w.writerows(rows)
for name in ('baseline','folded'):
    xs=[r['elapsed_ns'] for r in rows if r['variant']==name]
    print(name,'median elapsed batch ns',statistics.median(xs),'min',min(xs),'max',max(xs))
print('Measured AST evaluator cost only; not native-code or general compiler speed.')
