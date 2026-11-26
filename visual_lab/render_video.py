#!/usr/bin/env python3
"""Render step-by-step drawing video via PIL + ffmpeg."""
import os, sys, math, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from shapes import OBJECTS
from PIL import Image, ImageDraw, ImageFont

W,H = 800,600
OUT = os.path.join(os.path.dirname(__file__),'out','frames')
os.makedirs(OUT, exist_ok=True)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def draw_shape(dr, stype, p, color):
    if stype=='point': dr.ellipse([p['x']-4,p['y']-4,p['x']+4,p['y']+4],fill=color)
    elif stype=='line': dr.line([p['x1'],p['y1'],p['x2'],p['y2']],fill=color,width=3)
    elif stype=='curve':
        pts=[]
        for t in [i/20 for i in range(21)]:
            x=(1-t)**2*p['x1']+2*(1-t)*t*p['cx']+t*t*p['x2']
            y=(1-t)**2*p['y1']+2*(1-t)*t*p['cy']+t*t*p['y2']
            pts.append((x,y))
        dr.line(pts,fill=color,width=3)
    elif stype=='circle': dr.ellipse([p['cx']-p['r'],p['cy']-p['r'],p['cx']+p['r'],p['cy']+p['r']],outline=color,width=3)
    elif stype=='ellipse': dr.ellipse([p['cx']-p['rx'],p['cy']-p['ry'],p['cx']+p['rx'],p['cy']+p['ry']],outline=color,width=3)
    elif stype=='square': dr.rectangle([p['x'],p['y'],p['x']+p['s'],p['y']+p['s']],outline=color,width=3)
    elif stype=='rect': dr.rectangle([p['x'],p['y'],p['x']+p['w'],p['y']+p['h']],outline=color,width=3)
    elif stype=='triangle': dr.polygon([(p['x1'],p['y1']),(p['x2'],p['y2']),(p['x3'],p['y3'])],outline=color,width=3)
    elif stype=='poly':
        pts=[tuple(map(float,pt.split(','))) for pt in p['points'].split()]
        dr.polygon(pts,outline=color,width=3)

def render_video(obj_name, fps=4, hold=12):
    """Each step: draw progressively, hold ~hold frames, fade in new shape."""
    shapes = OBJECTS[obj_name]
    frames_dir = os.path.join(OUT,obj_name); os.makedirs(frames_dir,exist_ok=True)
    img = Image.new('RGB',(W,H),'white'); dr = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT,22)
    fnames=[]
    step_idx=0
    colors=['#1a1a2e','#e94560','#0f3460','#533483','#e76f51']
    for si,(stype,p,label,dep) in enumerate(shapes):
        color=colors[si%len(colors)]
        # draw this shape with "animation": reveal via partial for lines/curves
        if stype in ('line','curve'):
            # animate: draw partial then full
            for frac in [0.33,0.66,1.0]:
                tmp = img.copy(); td = ImageDraw.Draw(tmp)
                if stype=='line':
                    td.line([p['x1'],p['y1'],p['x1']+(p['x2']-p['x1'])*frac,p['y1']+(p['y2']-p['y1'])*frac],fill=color,width=3)
                else:
                    pts=[]
                    for t in [i/20*frac for i in range(int(21*frac)+1)]:
                        x=(1-t)**2*p['x1']+2*(1-t)*t*p['cx']+t*t*p['x2']
                        y=(1-t)**2*p['y1']+2*(1-t)*t*p['cy']+t*t*p['y2']
                        pts.append((x,y))
                    td.line(pts,fill=color,width=3)
                td.text((20,20),f'{obj_name} — step {si+1}/{len(shapes)}: {label}',font=font,fill='#666')
                fn=f'{frames_dir}/f{step_idx:04d}.png'; tmp.save(fn); fnames.append(fn); step_idx+=1
        else:
            # instant draw + hold
            draw_shape(dr,stype,p,color)
            dr.text((20,20),f'{obj_name} — step {si+1}/{len(shapes)}: {label}',font=font,fill='#666')
            for _ in range(hold):
                fn=f'{frames_dir}/f{step_idx:04d}.png'; img.save(fn); fnames.append(fn); step_idx+=1
    # final hold
    dr.text((20,580),f'{obj_name} — COMPLETE',font=font,fill='#333')
    for _ in range(hold*2):
        fn=f'{frames_dir}/f{step_idx:04d}.png'; img.save(fn); fnames.append(fn); step_idx+=1
    # encode
    out=os.path.join(os.path.dirname(OUT),f'{obj_name}_draw.mp4')
    lst=os.path.join(frames_dir,'list.txt')
    open(lst,'w').write(''.join(f"file '{f}'\nduration {1/fps}\n" for f in fnames)+f"file '{fnames[-1]}'\n")
    subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',lst,'-vf',f'fps={fps},format=yuv420p','-c:v','libx264','-preset','fast','-crf','20',out],capture_output=True)
    return out,len(fnames)

if __name__=='__main__':
    objs=sys.argv[1:] or list(OBJECTS.keys())
    for o in objs:
        v,n=render_video(o)
        print(f'{o}: {n} frames → {v}')
