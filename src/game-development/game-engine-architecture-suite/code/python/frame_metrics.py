"""Frame-time profiler CSV writer and nearest-rank quantile analysis (milliseconds)."""
import csv, math, statistics, sys

def quantile_nearest_rank(values,p):
    if not values or not 0 < p <= 1:
        raise ValueError('nonempty data and 0<p<=1 required')
    sorted_values=sorted(values)
    return sorted_values[math.ceil(p*len(values))-1]

def analyze(values, target_fps=60):
    if target_fps<=0: raise ValueError('positive FPS required')
    limit=1000/target_fps
    return dict(count=len(values),median=statistics.median(values),
        p95=quantile_nearest_rank(values,.95),p99=quantile_nearest_rank(values,.99),
        max=max(values),over_budget=sum(x>limit for x in values),budget_ms=limit)

def write_csv(path, values):
    with open(path,'w',newline='',encoding='utf8') as file:
        w=csv.writer(file);w.writerow(['frame','elapsed_ms'])
        w.writerows(enumerate(values))

if __name__ == '__main__':
    values=[13.5]*900+[17.0]*80+[28.0]*20
    write_csv('frames.csv',values)
    print(analyze(values))
