#!/usr/bin/env python3
"""WHITEBOARD — slow primitive-by-primitive drawing tutorial.
Each primitive animated: dot → extending line → arc sweep → etc."""
import os, sys, math, subprocess
from PIL import Image, ImageDraw, ImageFont

W,H = 960,640
FPS = 12
OUT = os.path.join(os.path.dirname(__file__),'out','wb_frames')
os.makedirs(OUT, exist_ok=True)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SMALL = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
MARKER = '#2b2b2b'
PAPER = '#f7f3ea'
ACCENT = '#c0392b'

def base(title):
    img = Image.new('RGB',(W,H),PAPER)
    dr = ImageDraw.Draw(img)
    dr.text((30,20),title,font=ImageFont.truetype(FONT,26),fill=MARKER)
    # subtle paper texture lines
    for y in range(60,H,40):
        dr.line([(0,y),(W,y)],fill='#e8e2d4',width=1)
    return img,dr

def txt(dr,s,x,y,size=18,color=MARKER,font=None):
    dr.text((x,y),s,font=font or ImageFont.truetype(SMALL,size),fill=color)

def arc_pts(cx,cy,r,a0,a1,n=60):
    return [(cx+r*math.cos(math.radians(a0+(a1-a0)*i/n)),
             cy+r*math.sin(math.radians(a0+(a1-a0)*i/n))) for i in range(n+1)]

def bezier(p0,p1,p2,n=60,t_max=1.0):
    pts=[]
    for i in range(n+1):
        t=t_max*i/n
        x=(1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0]
        y=(1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]
        pts.append((x,y))
    return pts

# each primitive returns list of PIL images
def prim_point():
    frames=[]
    img,dr = base('PRIMITIVE 1 — POINT')
    txt(dr,'A point is a position. No size. Just (x,y).',40,580)
    cx,cy=480,320
    for r in range(0,13):
        f=img.copy(); d=ImageDraw.Draw(f)
        d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=MARKER)
        d.line([(cx-30,cy),(cx+30,cy)],fill=ACCENT,width=1)
        d.line([(cx,cy-30),(cx,cy+30)],fill=ACCENT,width=1)
        txt(d,f'({cx},{cy})',cx+18,cy-10,16,ACCENT)
        frames.append(f)
    return frames

def prim_line():
    """Line: dot at start, extends x=0 → x=50 slowly (with axis)."""
    frames=[]
    img,dr = base('PRIMITIVE 2 — STRAIGHT LINE')
    txt(dr,'A dot at (0,0). Then the line extends x=0 → x=50.',40,580)
    # axis
    ax0,ay0,ax1 = 80,340,880  # x-axis pixel range
    dr.line([(ax0,ay0),(ax1,ay0)],fill=MARKER,width=2)
    # ticks 0..50
    for i in range(0,51,10):
        x=ax0+(ax1-ax0)*i/50
        dr.line([(x,ay0-5),(x,ay0+5)],fill=MARKER,width=2)
        txt(dr,str(i),x-8,ay0+10,14,MARKER)
    txt(dr,'x',ax1+10,ay0-25,20,MARKER)
    # start dot
    sx,sy=ax0,ay0
    d0=img.copy(); dd=ImageDraw.Draw(d0)
    dd.ellipse([sx-7,sy-7,sx+7,sy+7],fill=ACCENT)
    txt(dd,'start (0,0)',sx+12,sy-28,16,ACCENT)
    frames.append(d0)
    # extend slowly
    for step in range(1,121):
        t=step/120
        ex=sx+(ax1-sx)*t
        f=img.copy(); d=ImageDraw.Draw(f)
        # dot stays, line grows
        d.ellipse([sx-7,sy-7,sx+7,sy+7],fill=ACCENT)
        d.line([(sx,sy),(ex,sy)],fill=MARKER,width=4)
        # moving tip dot
        d.ellipse([ex-5,sy-5,ex+5,sy+5],fill=MARKER)
        # coordinate readout
        txt(d,f'x = {int(t*50)}',ex+10,sy-30,18,ACCENT)
        # axis+ticks redraw
        d.line([(ax0,ay0),(ax1,ay0)],fill='#999',width=1)
        for i in range(0,51,10):
            x=ax0+(ax1-ax0)*i/50
            d.line([(x,ay0-5),(x,ay0+5)],fill='#999',width=1)
            txt(d,str(i),x-8,ay0+10,14,'#999')
        frames.append(f)
    # end label
    f=img.copy(); d=ImageDraw.Draw(f)
    d.line([(sx,sy),(ax1,sy)],fill=MARKER,width=4)
    txt(d,'end (50,0) — length = 50 units',ax1-220,ay0-60,18,ACCENT)
    frames.append(f)
    return frames

def prim_curve():
    frames=[]
    img,dr = base('PRIMITIVE 3 — CURVED LINE')
    txt(dr,'A Bezier curve: start, control point (pulls the bend), end.',40,580)
    p0,p1,p2=(150,420),(480,120),(750,420)
    # draw control guides faintly first
    d0=img.copy(); dd=ImageDraw.Draw(d0)
    dd.line([p0,p1,p2],fill='#ccc',width=1)
    dd.ellipse([p0[0]-5,p0[1]-5,p0[0]+5,p0[1]+5],fill=ACCENT)
    dd.ellipse([p2[0]-5,p2[1]-5,p2[0]+5,p2[1]+5],fill=ACCENT)
    dd.ellipse([p1[0]-6,p1[1]-6,p1[0]+6,p1[1]+6],outline=ACCENT,width=2)
    txt(dd,'control',p1[0]-20,p1[1]-35,14,ACCENT)
    frames.append(d0)
    for step in range(1,121):
        f=img.copy(); d=ImageDraw.Draw(f)
        pts=bezier(p0,p1,p2,60,step/120)
        if len(pts)>1: d.line(pts,fill=MARKER,width=4,joint='curve')
        d.line([p0,p1,p2],fill='#ddd',width=1)
        d.ellipse([p0[0]-5,p0[1]-5,p0[0]+5,p0[1]+5],fill=ACCENT)
        d.ellipse([p2[0]-5,p2[1]-5,p2[0]+5,p2[1]+5],fill=ACCENT)
        d.ellipse([p1[0]-6,p1[1]-6,p1[0]+6,p1[1]+6],outline=ACCENT,width=2)
        frames.append(f)
    return frames

def prim_circle():
    """Circle via radius animation — compass sweep."""
    frames=[]
    img,dr = base('PRIMITIVE 4 — CIRCLE (radius sweep)')
    txt(dr,'Center point + radius arm rotates, tracing the circle.',40,580)
    cx,cy,r=480,330,200
    # center dot
    d0=img.copy(); dd=ImageDraw.Draw(d0)
    dd.ellipse([cx-6,cy-6,cx+6,cy+6],fill=MARKER)
    txt(dd,f'center ({cx},{cy})',cx+15,cy-10,16,MARKER)
    frames.append(d0)
    # radius arm + growing arc
    for step in range(1,181):
        ang=step/180*360
        f=img.copy(); d=ImageDraw.Draw(f)
        d.ellipse([cx-6,cy-6,cx+6,cy+6],fill=MARKER)
        # radius arm
        ex=cx+r*math.cos(math.radians(ang)); ey=cy+r*math.sin(math.radians(ang))
        d.line([(cx,cy),(ex,ey)],fill=ACCENT,width=2)
        d.ellipse([ex-4,ey-4,ex+4,ey+4],fill=ACCENT)
        # arc traced so far
        if step>1:
            pts=arc_pts(cx,cy,r,0,ang)
            d.line(pts,fill=MARKER,width=4,joint='curve')
        txt(d,f'r = {r}',cx+15,cy-30,16,ACCENT)
        frames.append(f)
    # complete
    f=img.copy(); d=ImageDraw.Draw(f)
    d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=MARKER,width=4)
    d.ellipse([cx-6,cy-6,cx+6,cy+6],fill=MARKER)
    txt(d,f'radius = {r} → diameter = {2*r}',cx-140,cy+r+30,18,ACCENT)
    frames.append(f)
    return frames

def prim_ellipse():
    frames=[]
    img,dr = base('PRIMITIVE 5 — ELLIPSE')
    txt(dr,'Circle stretched: rx ≠ ry. Same center, two radii.',40,580)
    cx,cy,rx,ry=480,330,240,130
    d0=img.copy(); dd=ImageDraw.Draw(d0)
    dd.ellipse([cx-6,cy-6,cx+6,cy+6],fill=MARKER)
    txt(dd,f'center ({cx},{cy})  rx={rx} ry={ry}',cx-120,cy-20,16,MARKER)
    frames.append(d0)
    for step in range(1,181):
        ang=step/180*360
        f=img.copy(); d=ImageDraw.Draw(f)
        ex=cx+rx*math.cos(math.radians(ang)); ey=cy+ry*math.sin(math.radians(ang))
        d.line([(cx,cy),(ex,ey)],fill=ACCENT,width=2)
        d.ellipse([ex-4,ey-4,ex+4,ey+4],fill=ACCENT)
        d.ellipse([cx-6,cy-6,cx+6,cy+6],fill=MARKER)
        if step>1:
            pts=[(cx+rx*math.cos(math.radians(a)),cy+ry*math.sin(math.radians(a))) for a in [i/60*ang for i in range(61)]]
            d.line(pts,fill=MARKER,width=4,joint='curve')
        frames.append(f)
    f=img.copy(); d=ImageDraw.Draw(f)
    d.ellipse([cx-rx,cy-ry,cx+rx,cy+ry],outline=MARKER,width=4)
    d.ellipse([cx-6,cy-6,cx+6,cy+6],fill=MARKER)
    txt(d,f'rx={rx} (wide)  ry={ry} (tall)',cx-110,cy+ry+25,18,ACCENT)
    frames.append(f)
    return frames

def prim_square():
    frames=[]
    img,dr = base('PRIMITIVE 6 — SQUARE')
    txt(dr,'4 equal sides, 90° angles. Top-left corner first.',40,580)
    x,y,s=330,180,240
    corners=[(x,y),(x+s,y),(x+s,y+s),(x,y+s)]
    d0=img.copy(); dd=ImageDraw.Draw(d0)
    dd.ellipse([x-6,y-6,x+6,y+6],fill=ACCENT)
    txt(dd,'start corner',x-60,y-30,16,ACCENT)
    frames.append(d0)
    # draw 4 sides sequentially
    for side in range(4):
        a,b=corners[side],corners[(side+1)%4]
        steps=40
        for st in range(1,steps+1):
            t=st/steps
            f=img.copy(); d=ImageDraw.Draw(f)
            # redraw previous sides fully
            for ps in range(side):
                pa,pb=corners[ps],corners[(ps+1)%4]
                d.line([pa,pb],fill=MARKER,width=4)
            # current side partial
            ex=a[0]+(b[0]-a[0])*t; ey=a[1]+(b[1]-a[1])*t
            d.line([a,(ex,ey)],fill=MARKER,width=4)
            d.ellipse([ex-5,ey-5,ex+5,ey+5],fill=MARKER)
            txt(d,f'side {side+1}/4 — length {s}',20,580,16,ACCENT)
            frames.append(f)
    return frames

def prim_rect():
    frames=[]
    img,dr = base('PRIMITIVE 7 — RECTANGLE')
    txt(dr,'Opposite sides equal. w ≠ h.',40,580)
    x,y,w,h=280,200,360,180
    corners=[(x,y),(x+w,y),(x+w,y+h),(x,y+h)]
    d0=img.copy(); dd=ImageDraw.Draw(d0)
    dd.ellipse([x-6,y-6,x+6,y+6],fill=ACCENT)
    txt(dd,f'w={w}  h={h}',x+10,y-30,16,ACCENT)
    frames.append(d0)
    for side in range(4):
        a,b=corners[side],corners[(side+1)%4]
        steps=35
        for st in range(1,steps+1):
            t=st/steps
            f=img.copy(); d=ImageDraw.Draw(f)
            for ps in range(side):
                pa,pb=corners[ps],corners[(ps+1)%4]
                d.line([pa,pb],fill=MARKER,width=4)
            ex=a[0]+(b[0]-a[0])*t; ey=a[1]+(b[1]-a[1])*t
            d.line([a,(ex,ey)],fill=MARKER,width=4)
            d.ellipse([ex-5,ey-5,ex+5,ey+5],fill=MARKER)
            frames.append(f)
    return frames

def prim_triangle():
    frames=[]
    img,dr = base('PRIMITIVE 8 — TRIANGLE')
    txt(dr,'3 vertices, 3 sides. Base first, then sides.',40,580)
    v=[(480,160),(260,440),(700,440)]
    d0=img.copy(); dd=ImageDraw.Draw(d0)
    for p in v: dd.ellipse([p[0]-5,p[1]-5,p[0]+5,p[1]+5],fill=ACCENT)
    txt(dd,'3 vertices marked',380,120,16,ACCENT)
    frames.append(d0)
    # draw 3 edges sequentially
    for side in range(3):
        a,b=v[side],v[(side+1)%3]
        steps=45
        for st in range(1,steps+1):
            t=st/steps
            f=img.copy(); d=ImageDraw.Draw(f)
            for ps in range(side):
                pa,pb=v[ps],v[(ps+1)%3]
                d.line([pa,pb],fill=MARKER,width=4)
            ex=a[0]+(b[0]-a[0])*t; ey=a[1]+(b[1]-a[1])*t
            d.line([a,(ex,ey)],fill=MARKER,width=4)
            d.ellipse([ex-5,ey-5,ex+5,ey+5],fill=MARKER)
            txt(d,f'edge {side+1}/3',20,580,16,ACCENT)
            frames.append(f)
    return frames

def prim_polygon():
    frames=[]
    img,dr = base('PRIMITIVE 9 — POLYGON (hexagon)')
    txt(dr,'n vertices → n sides. Regular hexagon here.',40,580)
    cx,cy,r=480,330,200
    v=[(cx+r*math.cos(math.radians(60*i)),cy+r*math.sin(math.radians(60*i))) for i in range(6)]
    d0=img.copy(); dd=ImageDraw.Draw(d0)
    for p in v: dd.ellipse([p[0]-5,p[1]-5,p[0]+5,p[1]+5],fill=ACCENT)
    txt(dd,'6 vertices on a circle',400,120,16,ACCENT)
    frames.append(d0)
    for side in range(6):
        a,b=v[side],v[(side+1)%6]
        steps=30
        for st in range(1,steps+1):
            t=st/steps
            f=img.copy(); d=ImageDraw.Draw(f)
            for ps in range(side):
                pa,pb=v[ps],v[(ps+1)%6]
                d.line([pa,pb],fill=MARKER,width=4)
            ex=a[0]+(b[0]-a[0])*t; ey=a[1]+(b[1]-a[1])*t
            d.line([a,(ex,ey)],fill=MARKER,width=4)
            d.ellipse([ex-5,ey-5,ex+5,ey+5],fill=MARKER)
            frames.append(f)
    return frames

def prim_pattern():
    frames=[]
    img,dr = base('PRIMITIVE 10 — GEOMETRIC PATTERN')
    txt(dr,'Repeat + transform: translate, rotate, scale.',40,580)
    # grid of circles appearing
    positions=[(x,y) for y in range(140,540,100) for x in range(140,820,100)]
    f=img.copy()
    for i,(x,y) in enumerate(positions):
        f=img.copy(); d=ImageDraw.Draw(f)
        for j,(px,py) in enumerate(positions[:i+1]):
            d.ellipse([px-18,py-18,px+18,py+18],outline=MARKER,width=3)
            if j==i: d.ellipse([px-4,py-4,px+4,py+4],fill=ACCENT)
        txt(d,f'{i+1}/{len(positions)} elements',20,580,16,ACCENT)
        frames.append(f)
    return frames

PRIMS = [
 ('01_point',prim_point),('02_line',prim_line),('03_curve',prim_curve),
 ('04_circle',prim_circle),('05_ellipse',prim_ellipse),('06_square',prim_square),
 ('07_rect',prim_rect),('08_triangle',prim_triangle),('09_polygon',prim_polygon),
 ('10_pattern',prim_pattern),
]

def main():
    all_lists=[]
    for name,fn in PRIMS:
        frames=fn()
        all_lists.append((name,frames))
        print(name,len(frames),'frames')
    # encode each segment then concat
    segs=[]
    for name,frames in all_lists:
        d=os.path.join(OUT,name); os.makedirs(d,exist_ok=True)
        lst=[]
        for i,f in enumerate(frames):
            p=os.path.join(d,f'f{i:04d}.png'); f.save(p); lst.append(p)
        listf=os.path.join(d,'list.txt')
        open(listf,'w').write(''.join(f"file '{p}'\nduration {1/FPS}\n" for p in lst)+f"file '{lst[-1]}'\n")
        seg=os.path.join(d,'seg.mp4')
        subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',listf,'-vf',f'fps={FPS},format=yuv420p','-c:v','libx264','-preset','fast','-crf','20',seg],capture_output=True)
        segs.append(seg)
        print('encoded',name)
    # concat all
    with open('/tmp/wb_list.txt','w') as fh:
        for s in segs: fh.write(f"file '{s}'\n")
    out=os.path.join(os.path.dirname(OUT),'WHITEBOARD_PRIMITIVES.mp4')
    subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i','/tmp/wb_list.txt','-c','copy',out],capture_output=True)
    print('DONE',out,os.path.getsize(out)//1024,'KB')

if __name__=='__main__': main()
