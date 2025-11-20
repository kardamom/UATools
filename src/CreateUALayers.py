#! python 3
import Rhino
import os
import sys
import System
import uuid
import json
import rhinoscriptsyntax as rs
import Eto.Drawing as drawing
import Eto.Forms as forms
from UAColorMap import color_to_rgb

def get_shared_resource_dir():
    id = System.Guid('8E8C234F-72DE-4D54-881C-3822ADF2ED52')
    plugin_file = Rhino.PlugIns.PlugIn.PathFromId(id)
    plugin_path = os.path.dirname(plugin_file)
    shared_dir = os.path.join(plugin_path, "shared")
    return shared_dir

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
            # Try multiple locations to find the JSON file
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # List of paths to try
            possible_paths = [
                os.path.join(get_shared_resource_dir(), "UALayers.json"), 
                os.path.join(script_dir, "UALayers.json"),# Same directory as script
            ]
     
            
            # Find the first existing path
            json_path = None
            for path in possible_paths:
                normalized_path = os.path.normpath(path)
                if os.path.exists(normalized_path):
                    json_path = normalized_path
                    break
            
            if json_path is None:
                print("Error: UALayers.json not found in any of these locations:")
                for path in possible_paths:
                    print("  - " + os.path.normpath(path))
                return None
        
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




class LayerSelectionDialog(forms.Dialog[bool]):
    """
    Eto Forms dialog for selecting layer categories.
    """
    def __init__(self, layer_keys):
        super(LayerSelectionDialog, self).__init__()
        
        self.Title = "Select UA Top Level Layers"
        self.Padding = drawing.Padding(10)
        self.Resizable = False
        
        self.layer_keys = [k for k in layer_keys if k.lower() != "default"]
        self.checkboxes = {}
        self.custom_file_path = None
        
        # Create layout
        layout = forms.DynamicLayout()
        layout.Spacing = drawing.Size(5, 5)
        
        # Add "All" checkbox
        self.check_all = forms.CheckBox()
        self.check_all.Text = "All"
        self.check_all.CheckedChanged += self.on_all_changed
        layout.AddRow(self.check_all)
        
        layout.AddRow(None)  # Spacer
        
        # Add checkbox for each layer
        for key in self.layer_keys:
            checkbox = forms.CheckBox()
            # Create display name (remove A- prefix)
            display_name = key
            checkbox.Text = display_name
            checkbox.CheckedChanged += self.on_checkbox_changed
            self.checkboxes[key] = checkbox
            layout.AddRow(checkbox)
        
        layout.AddRow(None)  # Spacer
        
        # Add custom file button
        file_button = forms.Button()
        file_button.Text = "Select Custom Layer File..."
        file_button.Click += self.on_file_button_click
        layout.AddRow(file_button)
        
        # Add OK and Cancel buttons
        self.DefaultButton = forms.Button()
        self.DefaultButton.Text = "OK"
        self.DefaultButton.Click += self.on_ok_clicked
        
        self.AbortButton = forms.Button()
        self.AbortButton.Text = "Cancel"
        self.AbortButton.Click += self.on_cancel_clicked
        
        button_layout = forms.DynamicLayout()
        button_layout.Spacing = drawing.Size(5, 5)
        button_layout.AddRow(None, self.DefaultButton, self.AbortButton)
        
        layout.AddRow(button_layout)
        
        self.Content = layout
    
    def on_all_changed(self, sender, e):
        """Handle 'All' checkbox change"""
        checked = self.check_all.Checked
        # Temporarily disable events to avoid recursion
        for checkbox in self.checkboxes.values():
            checkbox.CheckedChanged -= self.on_checkbox_changed
            checkbox.Checked = checked
            checkbox.CheckedChanged += self.on_checkbox_changed
    
    def on_checkbox_changed(self, sender, e):
        """Handle individual checkbox change"""
        # If all are checked, check 'All'
        # If any are unchecked, uncheck 'All'
        all_checked = all(cb.Checked for cb in self.checkboxes.values())
        # Temporarily disable event to avoid cascading
        self.check_all.CheckedChanged -= self.on_all_changed
        self.check_all.Checked = all_checked
        self.check_all.CheckedChanged += self.on_all_changed
    
    def on_file_button_click(self, sender, e):
        """Handle custom file selection"""
        dialog = forms.OpenFileDialog()
        dialog.Title = "Select Layer Definition JSON File"
        dialog.Filters.Add(forms.FileFilter("JSON Files", ".json"))
        
        if dialog.ShowDialog(self) == forms.DialogResult.Ok:
            self.custom_file_path = dialog.FileName
            print("Custom file selected: " + self.custom_file_path)
            # Close dialog with False to signal custom file selection
            self.Close(False)

    
    def on_ok_clicked(self, sender, e):
        """Handle OK button click"""
        self.Close(True)
    
    def on_cancel_clicked(self, sender, e):
        """Handle Cancel button click"""
        self.Close(False)
    
    def get_selections(self):
        """Return list of selected layer keys"""
        selected = []
        
        if self.check_all.Checked:
            selected.append("all")
        
        for key, checkbox in self.checkboxes.items():
            if checkbox.Checked:
                selected.append(key)
        
        return selected


def get_checkbox_options(layer_keys):
    """
    Present Eto dialog to the user based on available layer keys.
    Returns: (selections_list, custom_file_path) or (None, None) if cancelled
    """
    dialog = LayerSelectionDialog(layer_keys)
    result = dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
    
    if result:
        selections = dialog.get_selections()
        return selections, dialog.custom_file_path
    elif dialog.custom_file_path:
        # User selected a custom file
        return None, dialog.custom_file_path
    else:
        # User cancelled
        return None, None


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
                color = color_to_rgb(color)
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
            if isinstance(print_color, str):
                print_color = color_to_rgb(print_color)
            rs.LayerPrintColor(full_name, print_color)
        except Exception:
            pass
    else:

        try:
            black = rs.CreateColor((0,0,0))
            rs.LayerPrintColor(full_name, black)
        except Exception as ex:
            print ("FAILED to set color: {}".format(ex))
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
        print("Cannot proceed without layer structure file")#! python 3
