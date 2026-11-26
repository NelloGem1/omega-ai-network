# Shape primitives + object decompositions.
# Each object = ordered list of shapes. Each shape:
# (type, params, label, depends_on)
# Canvas: 800x600, origin top-left.

SHAPES = {
 'point':    {'params':['x','y'],'svg':'<circle cx="{x}" cy="{y}" r="4" fill="black"/>'},
 'line':     {'params':['x1','y1','x2','y2'],'svg':'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="black" stroke-width="3"/>'},
 'curve':    {'params':['x1','y1','cx','cy','x2','y2'],'svg':'<path d="M {x1} {y1} Q {cx} {cy} {x2} {y2}" fill="none" stroke="black" stroke-width="3"/>'},
 'circle':   {'params':['cx','cy','r'],'svg':'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="black" stroke-width="3"/>'},
 'ellipse':  {'params':['cx','cy','rx','ry'],'svg':'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="black" stroke-width="3"/>'},
 'rect':     {'params':['x','y','w','h'],'svg':'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="black" stroke-width="3"/>'},
 'square':   {'params':['x','y','s'],'svg':'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="none" stroke="black" stroke-width="3"/>'},
 'triangle': {'params':['x1','y1','x2','y2','x3','y3'],'svg':'<polygon points="{x1},{y1} {x2},{y2} {x3},{y3}" fill="none" stroke="black" stroke-width="3"/>'},
 'poly':     {'params':['points'],'svg':'<polygon points="{points}" fill="none" stroke="black" stroke-width="3"/>'},
}

def shape_to_svg(stype, params, color='black', fill='none'):
    s = SHAPES[stype]
    svg_tpl = s['svg'].replace('stroke="black"', f'stroke="{color}"').replace('fill="none"', f'fill="{fill}"')
    return svg_tpl.format(**params)

# OBJECTS — decomposed into ordered shapes
OBJECTS = {
 'bird': [
   ('ellipse',{'cx':400,'cy':320,'rx':90,'ry':70},'body oval','circle'),
   ('circle',{'cx':470,'cy':230,'r':55},'head circle','ellipse'),
   ('triangle',{'x1':525,'y1':230,'x2':580,'y2':245,'x3':525,'y3':260},'beak triangle','circle'),
   ('curve',{'x1':350,'y1':280,'cx':300,'cy':220,'x2':360,'y2':260},'left wing curve','ellipse'),
   ('curve',{'x1':450,'y1':280,'cx':500,'cy':220,'x2':440,'y2':260},'right wing curve','ellipse'),
   ('line',{'x1':380,'y1':390,'x2':370,'y2':470},'left leg','ellipse'),
   ('line',{'x1':420,'y1':390,'x2':430,'y2':470},'right leg','ellipse'),
   ('line',{'x1':360,'y1':470,'x2':390,'y2':470},'left foot','line'),
   ('line',{'x1':410,'y1':470,'x2':440,'y2':470},'right foot','line'),
   ('circle',{'cx':490,'cy':215,'r':6},'eye dot','circle'),
 ],
 'house': [
   ('square',{'x':280,'y':300,'s':240},'main walls square','point'),
   ('triangle',{'x1':250,'y1':300,'x2':520,'y2':300,'x3':385,'y3':160},'roof triangle','square'),
   ('rect',{'x':350,'y':400,'w':70,'h':140},'door rectangle','square'),
   ('rect',{'x':300,'y':340,'w':60,'h':50},'left window','square'),
   ('rect',{'x':410,'y':340,'w':60,'h':50},'right window','square'),
   ('line',{'x1':385,'y1':160,'x2':385,'y2':120},'chimney','triangle'),
   ('rect',{'x':370,'y':115,'w':30,'h':50},'chimney top','line'),
 ],
 'tree': [
   ('line',{'x1':400,'y1':520,'x2':400,'y2':320},'trunk line','point'),
   ('circle',{'cx':400,'cy':260,'r':110},'canopy circle 1','line'),
   ('circle',{'cx':310,'cy':300,'r':70},'canopy circle 2','circle'),
   ('circle',{'cx':490,'cy':300,'r':70},'canopy circle 3','circle'),
   ('ellipse',{'cx':400,'cy':500,'rx':90,'ry':20},'ground ellipse','line'),
 ],
 'sun': [
   ('circle',{'cx':400,'cy':300,'r':80},'sun body','point'),
   ('line',{'x1':400,'y1':140,'x2':400,'y2':180},'ray top','circle'),
   ('line',{'x1':400,'y1':420,'x2':400,'y2':460},'ray bottom','circle'),
   ('line',{'x1':240,'y1':300,'x2':280,'y2':300},'ray left','circle'),
   ('line',{'x1':520,'y1':300,'x2':560,'y2':300},'ray right','circle'),
   ('line',{'x1':287,'y1':187,'x2':315,'y2':215},'ray diag1','circle'),
   ('line',{'x1':485,'y1':385,'x2':513,'y2':413},'ray diag2','circle'),
   ('line',{'x1':513,'y1':187,'x2':485,'y2':215},'ray diag3','circle'),
   ('line',{'x1':315,'y1':385,'x2':287,'y2':413},'ray diag4','circle'),
 ],
 'fish': [
   ('ellipse',{'cx':360,'cy':300,'rx':110,'ry':60},'body ellipse','point'),
   ('triangle',{'x1':470,'y1':300,'x2':540,'y2':250,'x3':540,'y3':350},'tail triangle','ellipse'),
   ('circle',{'cx':320,'cy':285,'r':10},'eye','ellipse'),
   ('curve',{'x1':300,'y1':320,'cx':340,'cy':340,'x2':390,'y2':320},'mouth curve','ellipse'),
   ('line',{'x1':380,'y1':250,'x2':400,'y2':270},'fin 1','ellipse'),
   ('line',{'x1':400,'y1':250,'x2':420,'y2':270},'fin 2','ellipse'),
 ],
 'heart': [
   ('curve',{'x1':400,'y1':480,'cx':180,'cy':300,'x2':400,'y2':160},'left curve','point'),
   ('curve',{'x1':400,'y1':160,'cx':620,'cy':300,'x2':400,'y2':480},'right curve','curve'),
 ],
 'star': [
   ('poly',{'points':'400,120 440,260 590,260 470,340 520,480 400,400 280,480 330,340 210,260 360,260'},'5-point star','point'),
   ('circle',{'cx':400,'cy':300,'r':15},'center dot','poly'),
 ],
}

# PHASE PRIMITIVES — the 10 fundamentals with how-to + coords
PRIMITIVES = [
 ('point','A position with no size — the atom of drawing.','Place at (x,y). Everything starts here.'),
 ('line','Two points connected — straight path between them.','Draw from (x1,y1) to (x2,y2). Length = distance formula.'),
 ('curve','A line that bends — quadratic Bezier.','Start (x1,y1), control point (cx,cy) pulls the bend, end (x2,y2).'),
 ('circle','All points equidistant from center.','Center (cx,cy) + radius r. Proportions: width=height=2r.'),
 ('ellipse','Circle stretched on one axis.','Center (cx,cy), rx=horizontal radius, ry=vertical radius.'),
 ('square','4 equal sides, 90° angles.','Top-left (x,y), side s. Corners at (x,y),(x+s,y),(x+s,y+s),(x,y+s).'),
 ('rectangle','4 sides, opposite sides equal.','Top-left (x,y), width w, height h.'),
 ('triangle','3 points, 3 sides.','Vertices (x1,y1),(x2,y2),(x3,y3). Types: equilateral, isoceles, scalene.'),
 ('polygon','Closed shape with n straight sides.','List of vertex points in order.'),
 ('pattern','Repeated elements in sequence.','Array/loop of shapes with transforms (translate, rotate, scale).'),
]
