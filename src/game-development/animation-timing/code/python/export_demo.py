"""Emit a 60-frame exposure sheet and eased movement contact sheet CSV."""
import argparse, csv
from fractions import Fraction
from animation_time import FrameRate,on_twos,Cue,sample_position

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--prefix',default='shot01')
    args=p.parse_args()
    fps=FrameRate(24,1)
    sheet=on_twos(60)
    sheet.cues.extend([Cue('anticipation',0,8),Cue('primary action',8,42),
                       Cue('settle',42,60)])
    sheet.write_csv(args.prefix+'-exposure.csv',fps)
    with open(args.prefix+'-spacing.csv','w',newline='',encoding='utf-8') as f:
        w=csv.writer(f)
        w.writerow(['display_frame','seconds','position_px'])
        for frame in range(60):
            t=float(fps.time_at(frame))
            w.writerow([frame,round(t,6),round(sample_position(0,320,t,2.5),5)])
    print('Wrote exposure and spacing CSV files for',args.prefix)
if __name__=='__main__': main()
