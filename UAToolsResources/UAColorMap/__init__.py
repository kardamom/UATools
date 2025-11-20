#! python 3
"""
X11 Color Map Library
Provides standard X11 color names mapped to RGB tuples.
"""

def get_color_map():
    """
    Returns a dictionary of X11 color names mapped to RGB tuples.
    X11 color names are the standard color names used in X Window System,
    web browsers, and many graphics applications.
    """
    return {
        # Whites and near-whites
        "aliceblue": (240, 248, 255), "antiquewhite": (250, 235, 215),
        "azure": (240, 255, 255), "beige": (245, 245, 220),
        "bisque": (255, 228, 196), "blanchedalmond": (255, 235, 205),
        "cornsilk": (255, 248, 220), "floralwhite": (255, 250, 240),
        "ghostwhite": (248, 248, 255), "honeydew": (240, 255, 240),
        "ivory": (255, 255, 240), "lavenderblush": (255, 240, 245),
        "lemonchiffon": (255, 250, 205), "linen": (250, 240, 230),
        "mintcream": (245, 255, 250), "mistyrose": (255, 228, 225),
        "moccasin": (255, 228, 181), "navajowhite": (255, 222, 173),
        "oldlace": (253, 245, 230), "papayawhip": (255, 239, 213),
        "peachpuff": (255, 218, 185), "seashell": (255, 245, 238),
        "snow": (255, 250, 250), "wheat": (245, 222, 179),
        "white": (255, 255, 255), "whitesmoke": (245, 245, 245),
        
        # Grays
        "black": (0, 0, 0), "darkgray": (169, 169, 169),
        "darkgrey": (169, 169, 169), "darkslategray": (47, 79, 79),
        "darkslategrey": (47, 79, 79), "dimgray": (105, 105, 105),
        "dimgrey": (105, 105, 105), "gainsboro": (220, 220, 220),
        "gray": (128, 128, 128), "grey": (128, 128, 128),
        "lightgray": (211, 211, 211), "lightgrey": (211, 211, 211),
        "lightslategray": (119, 136, 153), "lightslategrey": (119, 136, 153),
        "slategray": (112, 128, 144), "slategrey": (112, 128, 144),
        "silver": (192, 192, 192),
        
        # Browns
        "brown": (165, 42, 42), "burlywood": (222, 184, 135),
        "chocolate": (210, 105, 30), "peru": (205, 133, 63),
        "rosybrown": (188, 143, 143), "saddlebrown": (139, 69, 19),
        "sandybrown": (244, 164, 96), "sienna": (160, 82, 45),
        "tan": (210, 180, 140),
        
        # Reds and pinks
        "red": (255, 0, 0), "crimson": (220, 20, 60),
        "darkred": (139, 0, 0), "firebrick": (178, 34, 34),
        "indianred": (205, 92, 92), "lightcoral": (240, 128, 128),
        "maroon": (128, 0, 0), "coral": (255, 127, 80),
        "darksalmon": (233, 150, 122), "lightpink": (255, 182, 193),
        "lightsalmon": (255, 160, 122), "pink": (255, 192, 203),
        "salmon": (250, 128, 114), "tomato": (255, 99, 71),
        "deeppink": (255, 20, 147), "hotpink": (255, 105, 180),
        "mediumvioletred": (199, 21, 133), "palevioletred": (219, 112, 147),
        
        # Oranges
        "orange": (255, 165, 0), "darkorange": (255, 140, 0),
        "orangered": (255, 69, 0),
        
        # Yellows
        "yellow": (255, 255, 0), "darkgoldenrod": (184, 134, 11),
        "gold": (255, 215, 0), "goldenrod": (218, 165, 32),
        "khaki": (240, 230, 140), "lightgoldenrodyellow": (250, 250, 210),
        "lightyellow": (255, 255, 224), "palegoldenrod": (238, 232, 170),
        
        # Greens
        "green": (0, 128, 0), "chartreuse": (127, 255, 0),
        "darkgreen": (0, 100, 0), "darkolivegreen": (85, 107, 47),
        "darkseagreen": (143, 188, 143), "forestgreen": (34, 139, 34),
        "greenyellow": (173, 255, 47), "lawngreen": (124, 252, 0),
        "lightgreen": (144, 238, 144), "lime": (0, 255, 0),
        "limegreen": (50, 205, 50), "mediumseagreen": (60, 179, 113),
        "mediumspringgreen": (0, 250, 154), "olive": (128, 128, 0),
        "olivedrab": (107, 142, 35), "palegreen": (152, 251, 152),
        "seagreen": (46, 139, 87), "springgreen": (0, 255, 127),
        "yellowgreen": (154, 205, 50),
        
        # Cyans
        "cyan": (0, 255, 255), "aqua": (0, 255, 255),
        "aquamarine": (127, 255, 212), "darkcyan": (0, 139, 139),
        "darkturquoise": (0, 206, 209), "lightcyan": (224, 255, 255),
        "lightseagreen": (32, 178, 170), "mediumaquamarine": (102, 205, 170),
        "mediumturquoise": (72, 209, 204), "paleturquoise": (175, 238, 238),
        "teal": (0, 128, 128), "turquoise": (64, 224, 208),
        
        # Blues
        "blue": (0, 0, 255), "cadetblue": (95, 158, 160),
        "cornflowerblue": (100, 149, 237), "darkblue": (0, 0, 139),
        "darkslateblue": (72, 61, 139), "deepskyblue": (0, 191, 255),
        "dodgerblue": (30, 144, 255), "lightblue": (173, 216, 230),
        "lightskyblue": (135, 206, 250), "lightsteelblue": (176, 196, 222),
        "mediumblue": (0, 0, 205), "mediumslateblue": (123, 104, 238),
        "midnightblue": (25, 25, 112), "navy": (0, 0, 128),
        "navyblue": (0, 0, 128), "powderblue": (176, 224, 230),
        "royalblue": (65, 105, 225), "skyblue": (135, 206, 235),
        "slateblue": (106, 90, 205), "steelblue": (70, 130, 180),
        
        # Purples and magentas
        "purple": (128, 0, 128), "blueviolet": (138, 43, 226),
        "darkmagenta": (139, 0, 139), "darkorchid": (153, 50, 204),
        "darkviolet": (148, 0, 211), "fuchsia": (255, 0, 255),
        "indigo": (75, 0, 130), "lavender": (230, 230, 250),
        "magenta": (255, 0, 255), "mediumorchid": (186, 85, 211),
        "mediumpurple": (147, 112, 219), "orchid": (218, 112, 214),
        "plum": (221, 160, 221), "thistle": (216, 191, 216),
        "violet": (238, 130, 238),
    }


def color_to_rgb(name):
    """
    Get RGB tuple for a color name.
    Returns (0, 0, 0) if color name not found.
    
    Args:
        name: Color name (case-insensitive)
    
    Returns:
        RGB tuple (r, g, b) where each value is 0-255
    """
    return get_color_map().get(name.lower(), (0, 0, 0))


def rgb_to_color(rgb):
    """Convert RGB tuple to color name from X11 color map"""
    # Get the inverse color map (RGB to name)
    color_map = get_color_map()
    
    # Look for exact match
    for name, rgb_value in color_map.items():
        if rgb == rgb_value:
            return name
    
    # Return as hex if no match
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"