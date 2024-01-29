# Author - Varun Ahlawat
''' 
Description - Takes in the arguments like height of the nose cone and the Haack constant for the Hack series, then 
creates a spline as a sketch that fits the curve geometry. Then an offset curve is added to the sketch 
Which is then closed to make an area enclosing curve. The enclosed area is then finally revolved around the axis.'''

import adsk.core, adsk.fusion, adsk.cam, traceback, math

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Prompt the user for cone height and Haack series constant (c)
        height_input = ui.inputBox('Enter cone height', 'Parameters', '')
        c_value_input = ui.inputBox('Enter Haack series constant (c)', 'Parameters', '')

        if not height_input or not c_value_input:
            return

        # Convert input strings to floats
        height = float(height_input[0])
        c_value = float(c_value_input[0])

        # Create the Haack cone
        create_haack_cone(height, c_value)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Function to create a cone based on Haack series
def create_haack_cone(height, c_value):
    app = adsk.core.Application.get()
    design = app.activeProduct

    # Get the root component of the active design
    root_comp = design.rootComponent

    # Create a new sketch on the XY plane
    sketches = root_comp.sketches
    xy_plane = root_comp.xYConstructionPlane
    sketch = sketches.add(xy_plane)

    # Calculate the radius at each point along the Haack series
    def haack_series(radius, c):
        return radius * math.sqrt(abs((c * 2 * math.pi) / (2 * math.pi * radius)))

    # Parameters for the Haack series
    base_radius = 1.0
    segments = 100

    # Create the Haack series profile
    fit_points = adsk.core.ObjectCollection.create()
    for i in range(segments + 1):
        angle = (2 * math.pi * i) / segments
        radius = base_radius * haack_series(abs(math.cos(angle)), c_value)
        fit_points.add(adsk.core.Point3D.create(radius * math.cos(angle), radius * math.sin(angle), 0))

    # Create a spline through the points
    spline = sketch.sketchCurves.sketchFittedSplines.add(fit_points)

    # Create an extrusion based on the sketch
    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    extrude_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(height))
    extrudes.add(extrude_input)