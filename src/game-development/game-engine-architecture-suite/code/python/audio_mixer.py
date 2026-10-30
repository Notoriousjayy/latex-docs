"""Deterministic 16-bit PCM synthesizer with clipping accounting."""
import math, struct, wave

def synthesize(seconds=0.25, rate=48_000):
    if seconds<=0 or rate<=0: raise ValueError('positive duration/rate required')
    output=[]
    clipped=0
    for i in range(round(seconds*rate)):
        t=i/rate
        mix=0.4*math.sin(2*math.pi*440*t)+0.25*math.sin(2*math.pi*660*t)
        if abs(mix)>1: clipped+=1
        output.append(round(max(-1,min(1,mix))*32767))
    return output,clipped

def write_wav(path,samples,rate=48_000):
    with wave.open(str(path),'wb') as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(rate)
        file.writeframes(struct.pack('<'+'h'*len(samples),*samples))

if __name__ == '__main__':
    s,clipped=synthesize()
    write_wav('voices.wav',s)
    print('wrote voices.wav; peak',max(abs(x) for x in s),'clipped',clipped)
