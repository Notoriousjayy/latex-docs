"""Original small CPU triangle rasterizer; writes uncompressed PPM, no dependencies."""
from pathlib import Path

def edge(a,b,p):
    return (p[0]-a[0])*(b[1]-a[1])-(p[1]-a[1])*(b[0]-a[0])

def render(width=96,height=96):
    if width<=0 or height<=0:
        raise ValueError('positive dimensions required')
    pix = [(12,20,35)]*(width*height)
    depth = [float('inf')]*(width*height)
    tris = [(((10,10,.8),(87,20,.8),(30,85,.8)),(30,85,190)),
            (((25,25,.2),(75,30,.2),(50,80,.2)),(230,140,60))]
    for (v0,v1,v2),rgb in tris:
        area=edge(v0,v1,v2)
        if abs(area)<1e-10:
            continue
        for y in range(height):
            for x in range(width):
                p=(x+0.5,y+0.5)
                w0=edge(v1,v2,p)/area
                w1=edge(v2,v0,p)/area
                w2=1-w0-w1
                if min(w0,w1,w2)<-1e-12:
                    continue
                z=w0*v0[2]+w1*v1[2]+w2*v2[2]
                idx=y*width+x
                if z<depth[idx]:
                    pix[idx]=rgb
                    depth[idx]=z
    return pix

def write_ppm(path, pix, width, height):
    with Path(path).open('wb') as f:
        f.write(f'P6\n{width} {height}\n255\n'.encode('ascii'))
        f.write(bytes(c for pixel in pix for c in pixel))

if __name__ == '__main__':
    write_ppm('triangle.ppm', render(),96,96)
    print('wrote triangle.ppm')
