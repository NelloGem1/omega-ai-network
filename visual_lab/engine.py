#!/usr/bin/env python3
"""VISUAL LEARNING ENGINE — decompose objects, generate step-by-step
instructions, render intermediate SVG frames + optional video."""
import os, sys, subprocess, html
sys.path.insert(0, os.path.dirname(__file__))
from shapes import OBJECTS, SHAPES, PRIMITIVES, shape_to_svg

OUT = os.path.join(os.path.dirname(__file__), 'out')
os.makedirs(OUT, exist_ok=True)
W,H = 800,600

def svg_frame(shapes_so_far, title=''):
    """Render cumulative SVG of shapes drawn so far."""
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
             '<rect width="800" height="600" fill="white"/>']
    for stype,params,label,color in shapes_so_far:
        parts.append(shape_to_svg(stype,params,color=color))
    if title:
        parts.append(f'<text x="20" y="30" font-family="sans-serif" font-size="16" fill="#666">{title}</text>')
    parts.append('</svg>')
    return ''.join(parts)

def generate_steps(obj_name):
    """PHASE 3: decompose → ordered instruction list with dependencies."""
    shapes = OBJECTS[obj_name]
    steps = []
    for i,(stype,params,label,dep) in enumerate(shapes):
        steps.append({
            'step': i+1, 'shape': stype, 'params': params,
            'label': label, 'depends_on': dep,
            'instruction': describe(stype,params,label),
            'color': '#1a1a2e' if i==0 else '#e94560' if 'eye' in label or 'dot' in label else '#0f3460',
        })
    return steps

def describe(stype,p,label):
    if stype=='circle': return f"Draw a circle centered at ({p['cx']},{p['cy']}) with radius {p['r']} — {label}."
    if stype=='ellipse': return f"Draw an ellipse centered at ({p['cx']},{p['cy']}), rx={p['rx']}, ry={p['ry']} — {label}."
    if stype=='square': return f"Draw a square at ({p['x']},{p['y']}) with side {p['s']} — {label}."
    if stype=='rect': return f"Draw a rectangle at ({p['x']},{p['y']}) size {p['w']}x{p['h']} — {label}."
    if stype=='triangle': return f"Draw a triangle with vertices ({p['x1']},{p['y1']}),({p['x2']},{p['y2']}),({p['x3']},{p['y3']}) — {label}."
    if stype=='line': return f"Draw a line from ({p['x1']},{p['y1']}) to ({p['x2']},{p['y2']}) — {label}."
    if stype=='curve': return f"Draw a curve from ({p['x1']},{p['y1']}) bending toward ({p['cx']},{p['cy']}) to ({p['x2']},{p['y2']}) — {label}."
    if stype=='poly': return f"Draw a polygon through points: {p['points']} — {label}."
    if stype=='point': return f"Mark point at ({p['x']},{p['y']}) — {label}."
    return f"Draw {stype} — {label}."

def render_object(obj_name):
    """PHASE 3+5: generate steps, render each intermediate frame."""
    steps = generate_steps(obj_name)
    frames = []
    drawn = []
    for step in steps:
        drawn.append((step['shape'],step['params'],step['label'],step['color']))
        svg = svg_frame(drawn, f"Step {step['step']}/{len(steps)}: {step['label']}")
        fn = os.path.join(OUT, f"{obj_name}_step{step['step']:02d}.svg")
        open(fn,'w').write(svg)
        frames.append(fn)
    # final combined
    final_svg = svg_frame(drawn, f"{obj_name} — complete")
    final_fn = os.path.join(OUT, f"{obj_name}_final.svg")
    open(final_fn,'w').write(final_svg)
    return steps, frames, final_fn

def make_contact_sheet(obj_name, frames):
    """Grid of all steps → single preview image via ImageMagick or ffmpeg."""
    # use ffmpeg tile filter on SVGs converted via rsvg? fallback: HTML page
    html_parts = ['<html><body style="background:#111;color:#eee;font-family:sans-serif">',
                  f'<h2>{obj_name} — step-by-step</h2><div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px">']
    for i,fn in enumerate(frames):
        html_parts.append(f'<div><div style="font-size:12px;margin-bottom:4px">Step {i+1}</div><img src="{os.path.basename(fn)}" style="width:100%;border:1px solid #444"></div>')
    html_parts.append('</div></body></html>')
    sheet = os.path.join(OUT, f'{obj_name}_steps.html')
    open(sheet,'w').write(''.join(html_parts))
    return sheet

if __name__=='__main__':
    objs = sys.argv[1:] or list(OBJECTS.keys())
    for obj in objs:
        steps, frames, final = render_object(obj)
        sheet = make_contact_sheet(obj, frames)
        print(f"{obj}: {len(steps)} steps → {len(frames)} frames + {os.path.basename(final)} + {os.path.basename(sheet)}")
