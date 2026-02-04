"""
Blender Python Script: Black Picnic Bench Generator
Run this script in Blender's Text Editor or via scripting workspace.
"""

import bpy
import math

def clear_scene():
    """Remove default objects."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_material(name, colour):
    """Create a simple material with the given colour."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = colour
    bsdf.inputs["Roughness"].default_value = 0.7
    return mat

def create_plank(name, dimensions, location, rotation=(0, 0, 0), material=None):
    """Create a single wooden plank (cuboid)."""
    bpy.ops.mesh.primitive_cube_add(location=location)
    plank = bpy.context.active_object
    plank.name = name
    plank.scale = (dimensions[0] / 2, dimensions[1] / 2, dimensions[2] / 2)
    plank.rotation_euler = rotation
    
    if material:
        plank.data.materials.append(material)
    
    # Apply scale to make further operations cleaner
    bpy.ops.object.transform_apply(scale=True)
    
    # Add bevel for slightly rounded edges
    bevel = plank.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.005
    bevel.segments = 2
    
    return plank

def create_picnic_bench():
    """Generate a complete picnic bench."""
    
    clear_scene()
    
    # Create black material
    black_wood = create_material("BlackWood", (0.02, 0.02, 0.02, 1.0))
    
    # Dimensions (in metres)
    plank_thickness = 0.04
    plank_width = 0.15
    table_length = 1.8
    table_width = 0.6
    seat_width = 0.3
    table_height = 0.75
    seat_height = 0.45
    leg_thickness = 0.08
    
    # Overhang of table/seats beyond the legs
    overhang = 0.15
    
    # Distance from centre to outer edge of seat
    seat_offset = (table_width / 2) + 0.05 + (seat_width / 2)
    
    all_objects = []
    
    # === TABLE TOP (2 planks) ===
    for i, y_offset in enumerate([-plank_width/2 - 0.01, plank_width/2 + 0.01]):
        plank = create_plank(
            name=f"TableTop_{i+1}",
            dimensions=(table_length, plank_width, plank_thickness),
            location=(0, y_offset, table_height),
            material=black_wood
        )
        all_objects.append(plank)
    
    # === SEATS (2 planks each side) ===
    for side in [-1, 1]:
        for i, y_inner in enumerate([-plank_width/2 - 0.01, plank_width/2 + 0.01]):
            y_pos = side * seat_offset + y_inner
            plank = create_plank(
                name=f"Seat_{'Front' if side == -1 else 'Back'}_{i+1}",
                dimensions=(table_length, plank_width, plank_thickness),
                location=(0, y_pos, seat_height),
                material=black_wood
            )
            all_objects.append(plank)
    
    # === A-FRAME LEGS (2 sets) ===
    leg_angle = math.radians(65)
    leg_length = (table_height + 0.1) / math.sin(leg_angle)
    
    for x_pos in [-(table_length/2 - overhang), (table_length/2 - overhang)]:
        for side in [-1, 1]:
            # Calculate leg position
            leg_base_y = side * 0.5
            
            plank = create_plank(
                name=f"Leg_{x_pos:.1f}_{side}",
                dimensions=(leg_thickness, leg_thickness, leg_length),
                location=(x_pos, leg_base_y, table_height / 2),
                rotation=(side * (math.pi/2 - leg_angle), 0, 0),
                material=black_wood
            )
            all_objects.append(plank)
    
    # === CROSS BRACES (horizontal support under table) ===
    for x_pos in [-(table_length/2 - overhang), (table_length/2 - overhang)]:
        brace = create_plank(
            name=f"CrossBrace_{x_pos:.1f}",
            dimensions=(leg_thickness, table_width + seat_width * 2 + 0.3, leg_thickness),
            location=(x_pos, 0, seat_height - 0.1),
            material=black_wood
        )
        all_objects.append(brace)
    
    # === CENTRE BRACE (lengthwise under table) ===
    centre_brace = create_plank(
        name="CentreBrace",
        dimensions=(table_length - 2 * overhang - leg_thickness, leg_thickness, leg_thickness),
        location=(0, 0, seat_height - 0.1),
        material=black_wood
    )
    all_objects.append(centre_brace)
    
    # === SEAT SUPPORTS ===
    for x_pos in [-(table_length/2 - overhang), (table_length/2 - overhang)]:
        for side in [-1, 1]:
            support = create_plank(
                name=f"SeatSupport_{x_pos:.1f}_{side}",
                dimensions=(leg_thickness, seat_width + 0.05, leg_thickness),
                location=(x_pos, side * seat_offset, seat_height - plank_thickness/2 - leg_thickness/2),
                material=black_wood
            )
            all_objects.append(support)
    
    # Select all bench parts and join them
    bpy.ops.object.select_all(action='DESELECT')
    for obj in all_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = all_objects[0]
    
    # Parent all objects to an empty for easy manipulation
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    parent_empty = bpy.context.active_object
    parent_empty.name = "PicnicBench"
    
    for obj in all_objects:
        obj.parent = parent_empty
    
    # Add a ground plane for context
    bpy.ops.mesh.primitive_plane_add(size=5, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    ground_mat = create_material("GroundMat", (0.3, 0.3, 0.3, 1.0))
    ground.data.materials.append(ground_mat)
    
    # Set up camera
    bpy.ops.object.camera_add(location=(3, -3, 2))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(65), 0, math.radians(45))
    bpy.context.scene.camera = camera
    
    # Add lighting
    bpy.ops.object.light_add(type='SUN', location=(2, -2, 5))
    sun = bpy.context.active_object
    sun.data.energy = 3
    sun.rotation_euler = (math.radians(45), math.radians(20), 0)
    
    print("Picnic bench created successfully!")
    return parent_empty

# Run the script
if __name__ == "__main__":
    create_picnic_bench()
