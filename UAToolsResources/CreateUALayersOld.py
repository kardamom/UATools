#! python 3
import Rhino
import os
import sys
import json
import rhinoscriptsyntax as rs


def load_layer_structure(custom_file=None):
    """
    Load the layer structure from JSON file.
    Returns the structure dict or None if loading fails.
    """
    try:
        if custom_file and os.path.exists(custom_file):
            json_path = custom_file
            print("Loading layer structure from custom file: " + json_path)
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(script_dir, "UALayers.json")
        
        if os.path.exists(json_path):
            if not custom_file:
                print("Loading layer structure from: " + json_path)
            with open(json_path, 'r') as file:
                return json.load(file)
        else:
            print("Error: No layer definition file found")
            return None
    except Exception as e:
        print("Error loading layer structure: " + str(e))
        return None


def get_checkbox_options(layer_keys):
    """
    Present checkboxes to the user based on available layer keys.
    If 'All' is checked, all other boxes are automatically checked.
    Returns: (selections_list, custom_file_path) or (None, None) if cancelled
    """
    go = Rhino.Input.Custom.GetOption()
    
    # Create 'All' toggle
    opt_all = Rhino.Input.Custom.OptionToggle(False, "No", "Yes")
    
    # Create toggles for each layer key (excluding 'Default' if present)
    layer_toggles = {}
    for key in layer_keys:
        if key.lower() != "default":  # Skip Default layer
            layer_toggles[key] = Rhino.Input.Custom.OptionToggle(False, "No", "Yes")
    
    custom_file = None
    go.AcceptNothing(True)
    
    while True:
        go.ClearCommandOptions()
        
        # Add 'All' option first
        go.AddOptionToggle("All", opt_all)
        
        # Add toggle for each layer
        for key in layer_keys:
            if key in layer_toggles:
                # Create friendly display name (remove A- prefix, replace underscores)
                #display_name = key.replace("A-", "").replace("_", "").replace("-", "")
                display_name = key.replace("A-", "").replace("_", "").replace("-", "").upper()

                #display_name = key.replace("A-", "A_").upper()
               
                go.AddOptionToggle(display_name, layer_toggles[key])
        
        # Add custom file option
        go.AddOption("LayerFile")
        
        result = go.Get()
        
        if result == Rhino.Input.GetResult.Option:
            option_index = go.OptionIndex()
            option_name = go.Option().LocalName
            
            # Handle custom file selection
            if option_name == "LayerFile":
                file_path = rs.OpenFileName("Select Layer Definition JSON File", 
                                            "JSON Files (*.json)|*.json||")
                if file_path:
                    custom_file = file_path
                    print("Custom file selected: " + custom_file)
                    # Reload structure and return to rebuild options
                    return None, custom_file
                continue
            
            # Handle 'All' toggle
            if option_index == 1 and opt_all.CurrentValue:
                for toggle in layer_toggles.values():
                    toggle.CurrentValue = True
            # If 'All' is checked and any individual option changes
            elif opt_all.CurrentValue and option_index != 1:
                # Check if all are still checked
                all_checked = all(toggle.CurrentValue for toggle in layer_toggles.values())
                if not all_checked:
                    opt_all.CurrentValue = False
            
            continue
        elif result == Rhino.Input.GetResult.Nothing:
            break
        else:
            return None, None
    
    # Collect selected options
    selected = []
    if opt_all.CurrentValue:
        selected.append("all")
    
    for key, toggle in layer_toggles.items():
        if toggle.CurrentValue:
            selected.append(key)
    
    return selected, custom_file


def build_uriu_layers(selections, structure):
    """
    Build the layer hierarchy based on user selections and loaded structure.
    """
    try:
        if not structure:
            print("Error: No layer structure available")
            return
        
        # Determine which layers to create
        layers_to_create = []
        
        if "all" in selections:
            # Create all layers except Default
            layers_to_create = [k for k in structure.keys() if k.lower() != "default"]
        else:
            # Create only selected layers
            layers_to_create = [s for s in selections if s in structure]
        
        if not layers_to_create:
            print("No layers selected to create.")
            return
        
        # Create the selected layers
        for layer_key in layers_to_create:
            if layer_key in structure:
                layer_spec = structure[layer_key]
                create_layer_from_spec(layer_key, layer_spec)
        
        print("URIU Architecture layer template created/updated successfully.")
        print("Created layers: " + ", ".join(layers_to_create))
        
    except Exception as e:
        print("Error creating layers: " + str(e))


def ensure_linetype(name):
    """
    Ensure a linetype exists. Rhino usually ships with Continuous/Dashed/Dotted.
    If Dashed/Dotted are missing, add simple patterns.
    """
    try:
        existing = rs.Linetypes()
        if existing and name in existing:
            return True
        if name == "Dashed":
            rs.AddLinetype("Dashed", [5.0, -5.0])
            return True
        if name == "Dotted":
            rs.AddLinetype("Dotted", [0.5, -2.0])
            return True
        if name == "Continuous":
            return True
    except Exception:
        pass
    return False


def get_or_create_layer(name, parent=None, linetype=None, print_width=None, print_color=None, color=None):
    """
    Create/ensure a layer (optionally under a parent). Then apply linetype/print settings.
    Returns the full layer path.
    """
    if parent and not rs.IsLayer(parent):
        rs.AddLayer(parent)

    full_name = name if parent is None else parent + "::" + name

    if not rs.IsLayer(full_name):
        rs.AddLayer(name, parent=parent)

    if color is not None:
        try:
            if isinstance(color, str):
                color = get_color_map().get(color.lower(), (0, 0, 0))
            rs.LayerColor(full_name, color)
        except Exception:
            pass

    if linetype:
        ensure_linetype(linetype)
        try:
            rs.LayerLinetype(full_name, linetype)
        except Exception:
            pass

    if print_color is not None:
        try:
            rs.LayerPrintColor(full_name, print_color)
        except Exception:
            pass

    if print_width is not None:
        try:
            rs.LayerPrintWidth(full_name, float(print_width))
        except Exception:
            pass

    return full_name


def create_layer_from_spec(name, spec, parent=None):
    """
    Create a layer from a name and specification.
    spec can be an empty dict (simple layer) or a dict with properties.
    """
    linetype = None
    print_width = None
    print_color = None
    color = None
    children = None
    
    if spec is not None and isinstance(spec, dict):
        linetype = spec.get("linetype")
        print_width = spec.get("print_width")
        print_color = spec.get("print_color")
        color = spec.get("color")
        children = spec.get("children")
    
    full_path = get_or_create_layer(name, parent=parent, linetype=linetype, 
                                    print_width=print_width, print_color=print_color, color=color)
    
    if children is not None and isinstance(children, dict):
        for child_name, child_spec in children.items():
            create_layer_from_spec(child_name, child_spec, parent=full_path)
    
    return full_path


def get_color_map():
    """
    Returns a dictionary of X11 color names mapped to RGB tuples.
    """
    return {
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
        "black": (0, 0, 0), "darkgray": (169, 169, 169),
        "darkgrey": (169, 169, 169), "darkslategray": (47, 79, 79),
        "darkslategrey": (47, 79, 79), "dimgray": (105, 105, 105),
        "dimgrey": (105, 105, 105), "gainsboro": (220, 220, 220),
        "gray": (128, 128, 128), "grey": (128, 128, 128),
        "lightgray": (211, 211, 211), "lightgrey": (211, 211, 211),
        "lightslategray": (119, 136, 153), "lightslategrey": (119, 136, 153),
        "slategray": (112, 128, 144), "slategrey": (112, 128, 144),
        "silver": (192, 192, 192), "brown": (165, 42, 42),
        "burlywood": (222, 184, 135), "chocolate": (210, 105, 30),
        "peru": (205, 133, 63), "rosybrown": (188, 143, 143),
        "saddlebrown": (139, 69, 19), "sandybrown": (244, 164, 96),
        "sienna": (160, 82, 45), "tan": (210, 180, 140),
        "red": (255, 0, 0), "crimson": (220, 20, 60),
        "darkred": (139, 0, 0), "firebrick": (178, 34, 34),
        "indianred": (205, 92, 92), "lightcoral": (240, 128, 128),
        "maroon": (128, 0, 0), "coral": (255, 127, 80),
        "darksalmon": (233, 150, 122), "lightpink": (255, 182, 193),
        "lightsalmon": (255, 160, 122), "pink": (255, 192, 203),
        "salmon": (250, 128, 114), "tomato": (255, 99, 71),
        "deeppink": (255, 20, 147), "hotpink": (255, 105, 180),
        "mediumvioletred": (199, 21, 133), "palevioletred": (219, 112, 147),
        "orange": (255, 165, 0), "darkorange": (255, 140, 0),
        "orangered": (255, 69, 0), "yellow": (255, 255, 0),
        "darkgoldenrod": (184, 134, 11), "gold": (255, 215, 0),
        "goldenrod": (218, 165, 32), "khaki": (240, 230, 140),
        "lightgoldenrodyellow": (250, 250, 210), "lightyellow": (255, 255, 224),
        "palegoldenrod": (238, 232, 170), "green": (0, 128, 0),
        "chartreuse": (127, 255, 0), "darkgreen": (0, 100, 0),
        "darkolivegreen": (85, 107, 47), "darkseagreen": (143, 188, 143),
        "forestgreen": (34, 139, 34), "greenyellow": (173, 255, 47),
        "lawngreen": (124, 252, 0), "lightgreen": (144, 238, 144),
        "lime": (0, 255, 0), "limegreen": (50, 205, 50),
        "mediumseagreen": (60, 179, 113), "mediumspringgreen": (0, 250, 154),
        "olive": (128, 128, 0), "olivedrab": (107, 142, 35),
        "palegreen": (152, 251, 152), "seagreen": (46, 139, 87),
        "springgreen": (0, 255, 127), "yellowgreen": (154, 205, 50),
        "cyan": (0, 255, 255), "aqua": (0, 255, 255),
        "aquamarine": (127, 255, 212), "darkcyan": (0, 139, 139),
        "darkturquoise": (0, 206, 209), "lightcyan": (224, 255, 255),
        "lightseagreen": (32, 178, 170), "mediumaquamarine": (102, 205, 170),
        "mediumturquoise": (72, 209, 204), "paleturquoise": (175, 238, 238),
        "teal": (0, 128, 128), "turquoise": (64, 224, 208),
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
        "purple": (128, 0, 128), "blueviolet": (138, 43, 226),
        "darkmagenta": (139, 0, 139), "darkorchid": (153, 50, 204),
        "darkviolet": (148, 0, 211), "fuchsia": (255, 0, 255),
        "indigo": (75, 0, 130), "lavender": (230, 230, 250),
        "magenta": (255, 0, 255), "mediumorchid": (186, 85, 211),
        "mediumpurple": (147, 112, 219), "orchid": (218, 112, 214),
        "plum": (221, 160, 221), "thistle": (216, 191, 216),
        "violet": (238, 130, 238),
    }


if __name__ == "__main__":
    # First load to get available layers
    structure = load_layer_structure()
    
    if structure:
        layer_keys = list(structure.keys())
        
        # Allow user to select different file if desired
        while True:
            user_selections, custom_file = get_checkbox_options(layer_keys)
            
            # If custom file was selected, reload and restart
            if custom_file and user_selections is None:
                structure = load_layer_structure(custom_file)
                if structure:
                    layer_keys = list(structure.keys())
                    continue
                else:
                    print("Failed to load custom file")
                    break
            
            # Process selections
            if user_selections is not None:
                print("User selected: " + ", ".join(user_selections))
                build_uriu_layers(user_selections, structure)
            else:
                print("No selections made or cancelled")
            break
    else:
        print("Cannot proceed without layer structure file")