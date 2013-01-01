
import json
import math

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
<svg id="chart" xmlns="http://www.w3.org/2000/svg" version="1.1" height="1024" width="1280">
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
                stroke-width:0;
                stroke:rgb(0,0,0);
                opacity:0.5;
            }
            a > rect.foo:hover, a > polygon.foo:hover {
                /*cursor: pointer;*/
                opacity:1.0;
                /*fill:rgb(255,196,196);*/
                fill:rgb(129, 159, 247); /* darker */
            }
            rect.plane {
                /*fill:rgb(220,220,255);*/
                stroke-width:1px;
                /*stroke:rgb(220,220,255);*/
                stroke:rgb(130,130,255);
                fill:rgb(255,255,255);
            }
            text.plane {
                font-size:24px;
            }
            .Unused {
                /*stroke-width:1px;*/
                /*stroke:rgb(220,220,255);*/
                fill:rgb(239, 245, 251);
            }
        ]]>
    </style>
    <!--polygon points="100,10 40,180 190,60 10,60 160,180"
        style="fill:lime;stroke:purple;stroke-width:5;fill-rule:evenodd;"-->
    <!--clipPath id="clip1">
        <rect x="0" y="0" width="60" height="50"/>
    </clipPath>
    <text clip-path="url(#clip1)" style="color:#ff0" dx="0" dy="12" font-size="23" x="6" y="6">text</text-->
    """

def foot():
    return """
    <!--text x="0" y="0" dx="0" dy="24" clip-path="" style="color:#ff0" font-size="24">jIQLW`,</text-->
</svg>
<script>
$(document).ready(function() {
    $('#chart');
});
</script>
</body>
</html>"""

def linesize(): return 16
def blocksize(): return linesize() ** 2

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

def children(ranges, rowheightpx, di):
    if not 'children' in di:
        return ''
    rowheightpx = rowheightpx / math.sqrt(math.sqrt(coderange(di))) - 1
    return ''.join(layout(ranges + [coderange(di), coderange(di['children'][0])],
                rowheightpx, di['children']))

# [(x,y,w,h),...]
def shape(sq, di):
    if (len(sq) == 1):
        (x,y,w,h) = sq[0]
        svg = """
        <rect class="foo %s" x="%.1f" y="%.1f" width="%.1f" height="%.1f">
            <title>%s (%s-%s)</title>
        </rect>
        """ % (cssclass(di['name']), x, y, w, h,
                di['name'], di['lo'], di['hi'])
        return linkwrap(svg, di)
    else:
        pts = []
        # 1st: top left, top right, bottom left
        (x,y,w,h) = sq[0]
        pts.append((x+w,y))
        pts.append((x,  y))
        pts.append((x,  y+h+1))
        # 2nd: top left
        (x,y,w,h) = sq[1]
        pts.append((x,  y))
        # last: bottom left, bottom right, top right
        (x,y,w,h) = sq[-1]
        pts.append((x,  y+h))
        pts.append((x+w,y+h))
        pts.append((x+w,y-1))
        # second to last if necessary
        (x2,y2,w2,h2) = sq[-2]
        if x2+w2 > x+w:
            pts.append((x2+w2,y2+h2))
        svg = """
        <polygon class="foo %s" stroke-width="0" points="%s">
            <title>%s (%s-%s)</title>
        </polygon>
        """ % (cssclass(di['name']),
               ' '.join('%g,%g' % (x,y) for x,y in pts), di['name'], di['lo'], di['hi'])
        return linkwrap(svg, di)

def single(ranges, rowheightpx, i, di):
    lo = int(di['lo'], 16)
    totalrange = ranges[-1]
    cr = coderange(di)
    bs = blocksize()
    ox = (int(lo / 65536) * bs) % (bs * 4)
    xx = float(lo) / linesize()
    oy = int(float(lo) / 0x40000) * bs
    w = float(cr) / linesize() if cr < 65536 else bs
    h = rowheightpx
    y = int((xx % (0x10000 / linesize())) / bs) * linesize()
    x = xx % bs 
    if oy == bs * 4:
        oy -= bs 
        ox = bs * 4
    #print 'totalrange=%u coderange=%u lo=%x xx=%u w=%u h=%g oy=%g y=%g' % (
            #totalrange, cr, lo, xx, w, h, oy, y)
    if 'children' in di:
        guts = children(ranges, rowheightpx, di)
        guts += """
        <text class="plane" x="%u" y="%u" dx="%.1f" dy="%.1f" text-anchor="middle">%s</text>
        """ % (ox + x, oy + y, (w-1)/2, (h-1)/2, di['name'])
    elif totalrange == 0x110000:
        guts = """
            <rect class="foo plane" x="%.1f" y="%.1f" width="%.1f" height="%.1f">
                <title>%s</title>
            </rect>
            <text class="plane" x="%u" y="%u" dx="%.1f" dy="%.1f" text-anchor="middle">%s</text>
            """ % (ox + x, oy + y, w-1, h-1,
                   di['name'],
                   ox + x, oy + y, (w-1)/2, (h-1)/2, di['name'])
    else:
        points = []
        will_overlap = x + w > bs
        while x + w > 0:
            ww = min(w, bs - x)
            w -= ww
            points.append((ox + x, oy + y, ww-1, h)) # + int(will_overlap and w > 0)))
            x = 0
            y += linesize()
        guts = shape(points, di)
    return """
        <g title="%s" class="tile">
            %s
        </g>""" % (di['name'],
               guts)

def layout(ranges, rowheightpx, data, pad=1):
    return ''.join(single(ranges, rowheightpx, i, di)
                    for i,di in enumerate(data))

if __name__ == '__main__':
    u = json.loads(open('unicode-codespace.json').read())
    #print codespace
    data = layout([coderange(u)], blocksize(), u['children'])
    print head() + data + foot()

