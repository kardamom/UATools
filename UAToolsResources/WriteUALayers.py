import rhinoscriptsyntax as rs
import json
from UAColorMap import rgb_to_color

def ExportLayerNamesJSON():
    # Get all layer names
    layers = rs.LayerNames()
    
    # Create the root structure
    layer_structure = {}
    
    # Process each layer
    for layer_name in layers:
        # Get layer properties
        layer_props = {}
        
        # Get color
        color = rs.LayerColor(layer_name)
        if color:        
             # Convert Color object to RGB tuple
            rgb = (color.R, color.G, color.B)
            color_name = rgb_to_color(rgb)
            
            if color_name != "black":  # Skip black (default)
                layer_props["color"] = color_name
        
        # Get print width
        print_width = rs.LayerPrintWidth(layer_name)
        if print_width and print_width != 0.0:
            layer_props["print_width"] = print_width
        
        # Get linetype
        linetype = rs.LayerLinetype(layer_name)
        if linetype and linetype.lower() != "continuous":
            layer_props["linetype"] = linetype
        
        # Split layer name by delimiter (:: for Rhino)
        parts = layer_name.split("::")
        
        # Navigate/create the nested structure
        current_level = layer_structure
        
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                # Last part - this is the actual layer
                if part not in current_level:
                    current_level[part] = layer_props if layer_props else {}
            else:
                # Intermediate part - create parent with children
                if part not in current_level:
                    current_level[part] = {"children": {}}
                elif "children" not in current_level[part]:
                    current_level[part]["children"] = {}
                
                current_level = current_level[part]["children"]
    
    # Save to JSON file
    filter = "JSON File (*.json)|*.json||"
    filename = rs.SaveFileName("Save layer structure as", filter)
    if not filename: return
    
    with open(filename, "w") as file:
        json.dump(layer_structure, file, indent=2)
    
    print(f"Layer structure exported to {filename}")


ExportLayerNamesJSON()