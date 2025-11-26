# UATools
Rhino toolbar and scripts for URIU Architecture. 

Intended as a place for URIU Architecture to collate and publish useful Python/Grasshopper/C# scripts.

<img width="235" height="157" alt="Screenshot 2025-11-25 at 07 19 14" src="https://github.com/user-attachments/assets/a76f187e-63ea-4479-93be-0060601d66f5" />

There are currently two commands:

### CreateUALayers
This loads a JSON file defining a layer structure. The user is asked to select which of the file's top level layers they want to create. Chosen layers are then created in the current Rhino document. Alternate JSON definition files can also be chosen.

<img width="200" height="318" alt="Screenshot 2025-11-25 at 07 19 35" src="https://github.com/user-attachments/assets/64fded22-2545-461a-84b7-2fd8ca81e458" />


### WriteUALayers
This writes the layers from the current Rhino document into user chosen file, in the JSON format recognized by CreateUALayers.

## Installation
Drag the [latest](release) .yak package into Rhino. The status bar should say 'UATools installed successfully'.

## Removal
Use Rhino's PackageManager to remove the toolbar.

<img width="807" height="596" alt="Screenshot 2025-11-26 at 08 26 26" src="https://github.com/user-attachments/assets/c7663105-93d1-4da5-99dd-a56b621ce998" />

## Editing
The toolbar is built using Rhino 8's ScriptEditor. Run the ScriptEditor command, then open the [UATools.rhproj](UATools.rhproj) with File/Open Project.

<img width="969" height="895" alt="Screenshot 2025-11-25 at 07 18 40" src="https://github.com/user-attachments/assets/a8729c9e-6173-4781-a9e4-cef78f742f21" />

## JSON
The definition [file](src/UALayers.json) recognizes hierarchies, layer colors, print colors, print widths. 

#### Notes
- use a print_width of -1 for layers you do not want printed
- do not use 'Hairline' as a width, instead pick an actual (mm) value
- color names are derived from X11 and defined in [UAColorMap](src/UAColorMap/__init__.py)

#### Example Snippet
```
  "A-SITE": {
    "color": "red",
    "children": {
      "A-HATCH": {
        "color": "#bebebe"
      },
      "A-TOPO": {
        "color": "darkgray"
      },
      "A-SITE BOUNDARY": {
        "color": "teal"
      },
      "A-RETAINING": {
        "color": "dimgray"
      },
      "A-CONTOUR": {},
      "A-SETBACK": {
        "color": "red",
        "print_width": 0.35
      },
      "A-BOUNDARY": {
        "color": "blue",
        "print_width": 0.5
      },
      "A-EASEMENT": {
        "color": "#ff7f7f",
        "print_width": 0.5
      }
    }
  }
```
