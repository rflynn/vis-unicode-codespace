
import json
import math

def blockswide(): return 5
def blockshigh(): return 4

def scale(): return 2

# pixels per line
# FIXME: also implicitly chars per column
def linesize(): return 16

def linewidth(): return linesize() ** 2

# number of lines per block
def blocksize(): return linesize() * 16

def head():
    return """<!doctype html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8"/>
    <!--script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js"></script-->
    <style type="text/css">
        body { margin:0 }
    </style>
</head>
<body>
<svg id="chart" xmlns="http://www.w3.org/2000/svg" version="1.1" width="%g" height="%g">
    <style type="text/css" >
        <![CDATA[
            @font-face {
                font-family: 'OpenSans Condensed';
                src: url('OpenSans-CondLight.ttf') format('truetype');
            }
            * {
                font-family: 'OpenSans Condensed','Helvetica Narrow','Arial Narrow',Tahoma,Arial,Helvetica,sans-serif;
                letter-spacing:-0.1em;
                font-weight:100;
            }
            .foo {
                fill:rgb(130,130,255);
                fill:rgb(206, 216, 246);
                stroke-width:0;
                stroke:rgb(0,0,0);
            }
            a > rect.foo:hover, a > polygon.foo:hover {
                /*cursor: pointer;*/
                opacity:1.0;
                /*fill:rgb(255,196,196);*/
                fill:rgb(169, 188, 245); /* darker */
            }
            rect.plane {
                /*fill:rgb(220,220,255);*/
                stroke-width:0px;
                /*stroke:rgb(220,220,255);*/
                stroke:rgb(130,130,255);
                stroke:rgb(0,0,0);
                fill:rgb(255,255,255);
                fill:rgb(239, 245, 251);
            }
            text.plane {
                font-size:%upx;
            }
            .Unused {
                /*stroke-width:1px;*/
                /*stroke:rgb(220,220,255);*/
                fill:rgb(239, 245, 251);
            }
        ]]>
    </style>
    """ % (blocksize() * blockswide() * scale(),
           blocksize() * blockshigh() * scale(),
           25 * scale())

def foot():
    return """
</svg>
<script>
$(document).ready(function() {
    $('#chart');
});
</script>
</body>
</html>"""


def pow2near(n): return int(math.log(n) / math.log(2))

def cssclass(s): return s.replace(' ', '-')

def coderange(d):
    hi = int(d['hi'], 16)
    lo = int(d['lo'], 16)
    return hi - lo + 1

def linkurl(di):
    if di['name'] == 'Unused':
        return None
    else:
        return 'http://www.unicode.org/charts/PDF/U%04X.pdf' % int(di['lo'],16)

def linkwrap(svg, di):
    url = linkurl(di)
    if url:
        svg = ('<a xlink:href="%s">' % url) + svg + '</a>'
    return svg

def children(ranges, h, di):
    if not 'children' in di:
        return ''
    return ''.join(layout(ranges + [coderange(di), coderange(di['children'][0])],
                h / math.sqrt(math.sqrt(coderange(di))), di['children']))

def serialize(x):
    if type(x) in [type(0.0),type(0)]: return '%g' % x
    if type(x) == type([]): return ' '.join(x)
    return '%s' % x

def tag(name, attr, contents=''):
    return '<%s %s>%s</%s>\n' % (
            name,
            ' '.join('%s="%s"' % (x,serialize(y)) for x,y in attr),
            contents,
            name)

# [(x,y,w,h),...]
def shape(sq, di):
    if (len(sq) == 1):
        (x,y,w,h) = sq[0]
        svg = tag('rect',
                [('class',['foo',cssclass(di['name'])]),
                 ('x', x),
                 ('y', y),
                 ('width', w),
                 ('height', h-1)],
                    tag('title', [],
                        '%s (%s-%s)' % (di['name'], di['lo'], di['hi'])))
        return linkwrap(svg, di)
    else:
        pts = []
        # 1st: top left, top right, bottom left
        (x,y,w,h) = sq[0]
        pts.append((x+w,y))
        pts.append((x,  y))
        pts.append((x,  y+h))
        # 2nd: top left
        (x,y,w,h) = sq[1]
        pts.append((x,  y))
        # last: bottom left, bottom right, top right
        (x,y,w,h) = sq[-1]
        pts.append((x,  y+h-1))
        pts.append((x+w,y+h-1))
        pts.append((x+w,y-1))
        # second to last if necessary
        (x2,y2,w2,h2) = sq[-2]
        if x2+w2 > x+w:
            pts.append((x2+w2,y2+h2-1))
        svg = tag('polygon',
                [('class',['foo',cssclass(di['name'])]),
                 ('points', ' '.join('%g,%g' % (x,y) for x,y in pts))],
                    tag('title', [],
                        '%s (%s-%s)' % (di['name'], di['lo'], di['hi'])))
        return linkwrap(svg, di)

def single(ranges, h, i, di):
    lo = int(di['lo'], 16)
    totalrange = ranges[-1]
    cr = coderange(di)
    bs = blocksize()
    # offset x: calculate the absolute x for the left side of a codeblock
    ox = (int(lo / 0x10000) * bs) % (bs * 4)
    # 
    xx = float(lo) / linesize()
    x = xx % bs
    # 
    oy = int(float(lo) / 0x40000) * bs
    w = float(cr) / linesize() if cr < 0x10000 else bs
    y = int((xx % (0x10000 / linesize())) / bs) * linesize()
    if oy == bs * 4:
        oy -= bs
        ox = bs * 4
    #print 'totalrange=%u coderange=%u lo=%x xx=%u w=%u h=%g oy=%g y=%g' % (
            #totalrange, cr, lo, xx, w, h, oy, y)
    if 'children' in di:

        guts = children(ranges, h, di)
        guts += tag('text',
                    [('class','plane'),
                     ('x', (ox + x) * scale()),
                     ('y', (oy + y) * scale()),
                     ('dx', (w * scale()) / 2),
                     ('dy', (h * scale()) / 2),
                     ('text-anchor', 'middle')],
                    di['name'])

    elif totalrange == 0x110000:

        anim = ''
        """
        if di['name'] == 'Plane 4':
            anim = tag('animateTransform',
                        [('attributeName','transform'),
                         ('type','scale'),
                         ('from','1'),
                         ('to','2'),
                         ('additive','replace'),
                         ('accumulate','sum'),
                         ('begin','0s'),
                         ('dur','1.0s'),
                         ('fill','freeze')])
                        #<animateTransform attributeName="transform"
                        #attributeType="XML" type="scale" from="1" to="3"
                        #additive="sum" begin="1s" dur="5s" fill="freeze"/>
        """

        guts = tag('rect',
                [('class',['foo','plane']),
                 ('x', (ox + x) * scale()),
                 ('y', (oy + y) * scale()),
                 ('width', w * scale() - 1),
                 ('height', h * scale() - 1),
                 ('onclick', """(function (evt){console.log(evt);evt.target.setAttribute('width','500px')})(evt)""")],
                    tag('title',[], di['name']) + anim) + \
                tag('text',
                    [('class', 'plane'),
                     ('x', (ox + x) * scale()),
                     ('y', (oy + y) * scale()),
                     ('dx', (w * scale()) / 2),
                     ('dy', (h * scale()) / 2),
                     ('text-anchor', 'middle')],
                    di['name'])

    else:
        points = []
        while x + w > 0:
            ww = min(w, bs - x)
            w -= ww
            points.append(
                ((ox + x) * scale(),
                 (oy + y) * scale(),
                 ww * scale() - 1,
                 h * scale()))
            x = 0
            y += linesize()
        guts = shape(points, di)
    return tag('g',
            [('title', di['name']),
             ('class', 'tile')],
            guts)

def layout(ranges, h, data, pad=1):
    return ''.join(single(ranges, h, i, di)
                    for i,di in enumerate(data))

if __name__ == '__main__':
    u = json.loads(open('unicode-codespace.json').read())
    #print codespace
    node = u
    data = layout([coderange(node)], blocksize(), node['children'])
    print head() + data + foot()

