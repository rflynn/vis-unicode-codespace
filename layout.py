
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
<svg id="chart" xmlns="http://www.w3.org/2000/svg" version="1.1" height="4096" width="4096">
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
            rect.foo { 
                fill:rgb(130,130,255);
                stroke-width:0;
                stroke:rgb(0,0,0);
                opacity:0.2;
            }
            rect.foo:hover {
                cursor: pointer;
                opacity:1.0;
            }
            text.plane {
                font-size:24px;
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

"""

data [{hi,lo,name},...]

coderange       1m  64k
rowheightpx     256 16

cellrange       64k 256-32

"""

def pow2near(n): return int(math.log(n) / math.log(2))

def coderange(d):
    hi = int(d['hi'], 16)
    lo = int(d['lo'], 16)
    return hi - lo + 1

def children(ranges, rowheightpx, di):
    if not 'children' in di:
        return ''
    rowheightpx = rowheightpx / math.sqrt(math.sqrt(coderange(di))) - 1
    return ''.join(layout(ranges + [coderange(di), coderange(di['children'][0])],
                rowheightpx, di['children']))

def single(ranges, rowheightpx, i, di):
    lo = int(di['lo'], 16)
    totalrange = ranges[-1]
    cr = coderange(di)
    ox = (int(lo / 65536) * 256) % 1024
    xx = float(lo) / 16
    oy = int(float(lo) / 0x40000) * 256
    w = float(cr) / 16 if cr < 65536 else 256
    h = rowheightpx
    y = int((xx % (0x10000 / 16)) / 256) * 16
    x = xx % 256
    #print 'totalrange=%u coderange=%u lo=%x hi=%x xx=%u w=%u' % (totalrange, cr, lo, hi, xx, w)
    if 'children' in di:
        guts = children(ranges, rowheightpx, di)
    elif totalrange == 0x110000:
        guts = """
            <rect class="foo" x="%.1f" y="%.1f" width="%.1f" height="%.1f" />
            <text class="plane" x="%u" y="%u" dx="%.1f" dy="%.1f" text-anchor="middle">%s</text>
            """ % (ox + x, oy + y, w-1, h-1,
                   ox + x, oy + y, (w-1)/2, (h-1)/2, di['name'])
    else:
        guts = ''
        will_overlap = x + w > 256
        while x + w > 0:
            ww = min(w, 256 - x)
            w -= ww
            guts += '<rect class="foo" x="%.1f" y="%.1f" width="%.1f" height="%.1f" />' % (
                ox + x, oy + y, ww-1, h + int(will_overlap and w > 0))
            x = 0
            y += 16
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
    data = layout([coderange(u)], 256, u['children'])
    print head() + data + foot()

