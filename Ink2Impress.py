"""\
Ink2Impress.py

Create impress.js presentation graphically in Inkscape!

Still WIP, but can already create some awesome stuff!

Known Issues:
	3) Some resolution issues
"""

from lxml import etree
import re
import math

import matutil
from matutil import E_X, E_Y, Matrix, scale_matrix, rotation_matrix, eye, translation_matrix

TRANSFORM_MATRIX_PAT = r"matrix\(([^,]*),([^,]*),([^,]*),([^,]*),([^,]*),([^,]*)\)"
TRANSFORM_TRANSLATE_PAT = r"translate\(([^,]*),([^,]*)\)"
TRANSFORM_SCALE_PAT = r"scale\(([^,]*),([^,]*)\)"

BASE_WIDTH      = 900
BASE_HEIGHT     = 600

ID_OVERVIEW = "overview"

class Rect(object):
    def __init__(self, x=0, y=0, h=0, w=0, r=0, id_=None, element=None, transform=None):
        if element is not None:
            self._init_from_element(element, transform)
        else:
            self._x = x
            self._y = y
            self._h = h
            self._w = w
            self._id = id_
            self._r = r
            
    def _init_from_element(self, element, transform):
        # Define transform-independant parameters
        if element.get("id"):
            self._id = element.get("id")
        else:
            self._id = None
            
        # Init all the params that might be affected by the transformation
        if element.get("x"):
            self._x = float(element.get("x"))
        else:
            self._x = 0
            
        if element.get("y"):
            self._y = float(element.get("y"))
        else:
            self._y = 0
            
        if element.get("height"):
            self._h = float(element.get("height"))
        else:
            self._h = 0
            
        if element.get("width"):
            self._w = float(element.get("width"))
        else:
            self._w = 0
           
        # Get the transform of the element
        if transform:
            self._transform = transform
        else:
            self._transform = get_element_transform(element)
            
        # Apply the transformation to all properties
        # Get the rotation
        r = self._r = self._transform.r
        
        # Get the scale and apply to width and height
        self._w = w = self._w * self._transform.sx
        self._h = h = self._h * self._transform.sy
        # Calculate new x and y coordinates
        x_center = self._x + (w / 2)
        y_center = self._y + (h / 2)
        
        x, y = rotate(x_center, y_center, r)
        x += self._transform.dx
        y += self._transform.dy
        
        self._x = x
        self._y = y
        
        # Try and change the rotation based on rotation-direction and rotation-extra
        # attributes
        rotation_direction = get_attribute(element, "rotation-direction", inherit=True)
        rotation_extra = get_attribute(element, "rotation-extra", inherit=True)
        
        # Set rotation direction
        if rotation_direction:
            if rotation_direction.lower() == "cw":
                # Make sure r is clockwise
                r = r % (math.pi * 2)
            elif rotation_direction.lower() == "ccw":
                # Make r counter-clockwise
                r = r % (-(math.pi * 2))
            
        # Set rotation extra
        if rotation_extra is not None:
            rotation_extra = int(rotation_extra)
            r += (math.pi * 2) * rotation_extra
            
        # Set the rotation
        self._r = r
            
    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y
    
    @property
    def width(self):
        return self._w
    
    @property
    def w(self):
        return self.width
    
    @property
    def height(self):
        return self._h
    
    @property
    def h(self):
        return self.height
    
    @property
    def id(self):
        return self._id
    
    @property
    def rotation(self):
        return math.degrees(self._r)
    
    @property
    def r(self):
        return self.rotation
        
class Transform(object):
    def __init__(self, matrix=None):
        if not matrix:
            matrix = eye(3)
        self._matrix = matrix
        
    def __add__(self, other):
        return Transform(other._matrix * self._matrix)
    
    @property
    def dx(self):
        return self._matrix[(0, 2)]
    
    @property
    def dy(self):
        return self._matrix[(1, 2)]
        
    @property
    def r(self):
        return matutil.decompose_rotation2(self._matrix.minor(2, 2))
        
    @property
    def sx(self):
        return matutil.decompose_scale(self._matrix.minor(2, 2))[0]
        
    @property
    def sy(self):
        return matutil.decompose_scale(self._matrix.minor(2, 2))[1]
    
def rotate(x, y, r):
    rot_mat = rotation_matrix(2, 0, 1, r)
    vec = x * E_X + y * E_Y
    vec_tag = rot_mat * vec
    x = vec_tag[(0, 0)]
    y = vec_tag[(1, 0)]
    
    return x, y
    
    
def scale_transform(sx, sy):
    return Transform(scale_matrix(sx, sy, 1))
    
def rotation_transform(r):
    return Transform(rotation_matrix(3, 0, 1, r))
    
def translate_transform(dx, dy):
    return Transform(translation_matrix(dx, dy))

def parse_matrix(mat):
    matrix_parts = re.match(TRANSFORM_MATRIX_PAT, mat).groups()
    matrix_parts = [float(part) for part in matrix_parts]
    a, b, c, d, e, f = matrix_parts
    matrix = Matrix([[a, c, e],
                     [b, d, f],
                     [0,0, 1]])
    
    return Transform(matrix)

def parse_translate(trans):
    translate_parts = re.match(TRANSFORM_TRANSLATE_PAT, trans).groups()
    
    x = float(translate_parts[0])
    y = float(translate_parts[1])
    
    return translate_transform(x, y)

def parse_scale(scale):
    scale_parts = re.match(TRANSFORM_SCALE_PAT, scale).groups()
    scale_parts = [float(part) for part in scale_parts]
    return scale_transform(scale_parts[0], scale_parts[1])


def parse_transform(value):
    """Parse the 'transform=' attribute of SVG tags.
    Return (r, x, y)
    """
    for parser in [parse_translate, parse_matrix, parse_scale]:
        try:
            return parser(value)
        except TypeError:
            raise
        except:
            pass
    return Transform(eye(3))
    
def calc_scale(base_width, base_height, width, height):
    width_scale = width / base_width
    height_scale = height / base_height
    
    scaled_height_diff = (height / width_scale) - base_height
    scaled_width_diff = (width / height_scale) - base_width
    
    if scaled_width_diff > scaled_height_diff:
        return width_scale
    else:
        return height_scale
    
def get_element_transform(element):
    try:
        return parse_transform(element.get("transform"))
    except:
        return Transform()
    
def is_ancestor(ancestor, decendant):
    if ancestor not in list(decendant.iterancestors()):
        return False
    return True

def is_decendant(decendant, ancestor):
    return is_ancestor(ancestor, decendant)
    
def sum_parent_transform(element, topmost, include_self=True):
    # First, make sure element is a decendant of topmost
    if topmost not in list(element.iterancestors()):
        raise ValueError("%s is not a decendant of %s" % (element, topmost))
        
    transform = Transform()
    if include_self:
        transform += get_element_transform(element)
    for ancestor in element.iterancestors():
        cur_transform = get_element_transform(ancestor)
        transform += cur_transform
        
        if ancestor == topmost:
            break
    return transform

def inherit_attribute(element, attrib, topmost=None):
    """Inherit attribute 'attrib' from closest parent possible.
    """
    if (topmost is not None) and not is_ancestor(topmost, element):
        raise ValueError("%s is not an ancestor of %s" % (topmost, element))
        
    inherited_attrib = None
    #NOTE: assume ancestors are iterated from closest to farthest parent
    for ancestor in element.iterancestors():
        inherited_attrib = ancestor.get(attrib)
        if inherited_attrib is not None:
            return inherited_attrib
        
def get_attribute(element, attrib, inherit=False, topmost=None):
    if element.get(attrib) is not None:
        return element.get(attrib)
    else:
        return inherit_attribute(element, attrib, topmost)
    
def process_layout_layer(layout_layer):
    # First, we want to get all the rects in the layer
    #BUG: for now, we are assumins that there is only 1 rect per group!
    rects = layout_layer.xpath(".//rect")
    
    # Get the parent-induced transformation for all rects
    parent_transforms = [sum_parent_transform(rect, layout_layer) for rect in rects]
    
    # Parse all the rects, and apply transformations
    rect_objects = [
        Rect(element=rect, transform=transform) for
            rect, transform in zip(rects, parent_transforms)
        ]
    
    #TODO: this will be the place to add metadata based filtering!
    
    # Now we have proper frame data to return!
    return rect_objects

def _apply_opacity(color, opacity, back_color="#FFFFFF", max_opacity=1.0):
    parse_color = lambda color: [ord(c) for c in color[1:].decode("hex")]
    calc_color = lambda c, b_c: ((c * opacity) + (b_c * (max_opacity - opacity))) / max_opacity
    rgb = parse_color(color)
    back_rgb = parse_color(back_color)
    result_rgb = [calc_color(c, b_c) for c, b_c in zip(rgb, back_rgb)]
    rgb_triplet = "".join(chr(int(c)) for c in result_rgb)
    color_string = "#" + rgb_triplet.encode("hex")
    return color_string

def get_background_color(svg_root):
    expr = "*[local-name() = $name]"
    namedview = svg_root.xpath(expr, name = "namedview")[0]
    pagecolor = namedview.get("pagecolor")
    pageopacity = namedview.get("{%s}pageopacity" % (namedview.nsmap["inkscape"], ))
    try:
        pageopacity = float(pageopacity)
        pagecolor = _apply_opacity(pagecolor, pageopacity)
    except:
        pass
    
    return pagecolor

def create_impress(svg_tree):
    # Get the <svg> node
    
    svg_root = svg_tree.getroot()
    
    # Get all layers (<g> nodes under the <svg> node)
    # First layer is the graphics, the second is the layout.
    layers = svg_root.xpath("g")
    graphics_layer = layers[0]
    layout_layer = layers[1]
    
    # Get the page color
    pagecolor = get_background_color(svg_root)
    
    # Get all the frame-rects from the layout layer, correctly transformed!
    step_rects_data = process_layout_layer(layout_layer)
    
    # Set sizes for scaling
    base_width = BASE_WIDTH
    base_height = BASE_HEIGHT
    
    # Create a <div> from each layout <rect>
    divs = []
    for data in step_rects_data:
        scale = calc_scale(base_width, base_height, data.w, data.h)
        rotate = data.r
        # Here we add the location of the layout layer to compensate for
        # its translations.
        #TODO: Do we need to handle rotation and scale?
        x = data.x
        y = data.y
        div = etree.Element("div")
        div.set("data-scale",str(scale))
        div.set("data-rotate", str(rotate))
        div.set("data-x", str(x))
        div.set("data-y", str(y))
        div.set("class", "step")
        div.set("id", data.id)
        # Add empty data - cause we have to...
        # Don't make a clickable span for the overview
        if data.id != ID_OVERVIEW:
            span = etree.Element("span", style="width:%dpx;height:%dpx;display:block" % (data.w / scale, data.h / scale, ))
        else:
            span = etree.Element("span", style="width:%dpx;height:%dpx;" % (data.w / scale, data.h / scale, ))
        span.text = " "
        div.append(span)
        divs.append(div)
        
    # Wrap the graphics layer in a <div> tag, use the width and height of the <svg> tag.
    graphics_wrapper_text = (
        '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="%s" height="%s"></svg>' %
         (svg_root.get("width"), svg_root.get("height"))
         )
    graphics_div = etree.fromstring(graphics_wrapper_text)
    graphics_div.append(graphics_layer)
    
    # Put all <div>s in a nice HTML page
    
    # Build the HTML template
    base_html_text = """\
<html>
    <head>
    </head>
    <body>
    
        <div id="impress">
        </div>
    
        <script type="text/javascript" src="js/impress.js">;</script>
    </body>
</html>\
"""
    base_html = etree.fromstring(base_html_text)
    
    # Add background color
    if pagecolor:
        body_tag = base_html.xpath("body")[0]
        body_tag.set("style", "background-color:%s;" % (pagecolor, ))
    
    # Get the impress <div>
    impress_div = base_html.xpath("//div")[0]
    
    # Append all layout <div> nodes into the impress one
    for div in divs:
        impress_div.append(div)
        
    # Append the graphics <div> too
    impress_div.append(graphics_div)
    
    # String-ize the result and return it
    # Don't forget the <!doctype html> !
    result_text = "<!doctype html>\n" + etree.tostring(base_html, pretty_print=True)
    return result_text

def main():
    import sys
    
    if len(sys.argv) != 3:
        print "Usage: %s <source_svg> <target_html>" % (sys.argv[0],)
        return
    
    #HACK: removing the xmlns issue...
    svg_text = open(sys.argv[1]).read()
    svg_text = svg_text.replace('xmlns="http://www.w3.org/2000/svg"', "", 1)
    svg_root = etree.fromstring(svg_text)
    svg_tree = svg_root.getroottree()
        
    #svg_tree = etree.parse(sys.argv[1])
    html_text = create_impress(svg_tree)
    open(sys.argv[2], "wb").write(html_text)

if __name__ == '__main__':
    main()
    
    