import numpy as np
import trimesh
import os
import laspy
import networkx as nx


def get_floorplan_from_mesh(mesh):
    G = nx.Graph()

    for a, b in mesh.edges:
        ca, cb = mesh.vertices[a,2], mesh.vertices[b,2]
        if ca < 0.01 and cb < 0.01:
            G.add_edge(tuple(mesh.vertices[a,:2]), tuple(mesh.vertices[b,:2]))
    floorplan = nx.cycle_basis(G)

    # Make round
    floorplan = [part + [part[0]] for part in floorplan]
    # To list
    return [[list(node) for node in part] for part in floorplan]


def get_item(id):
    """_summary_

    Args:
        id (str): filename in form of minimal_house_#

    Returns:
        trimesh.Trimesh, trimesh.Trimesh, shapely.multipolygon, shapely.multipolygon, laspy : wall, roof, floorplan, outline, pcd
    """
    like_bag_root = '2.5D'
    pcd_root = 'clouds'
    gt_root = 'references'

    # Load floorplan
    gt_mesh = trimesh.exchange.load.load(os.path.join(gt_root, id + '.obj'), force='mesh')
    floorplan = get_floorplan_from_mesh(gt_mesh)

    # Load roof and wall
    building = trimesh.exchange.load.load(os.path.join(like_bag_root, id + '.obj'))
    for t in building.geometry.values():
        if np.array_equal(t.visual.material.main_color, np.array([255, 255, 255, 255])):
            wall = t
        elif np.array_equal(t.visual.material.main_color, np.array([255, 0, 0, 255])):
            roof = t

    # Load outline
    building25 = trimesh.util.concatenate(wall, roof)
    outline = trimesh.path.polygons.projected(building25, normal=[0,0,1])
    outline = np.round(np.array(outline.exterior.xy).T, 3).reshape(1,-1, 2).tolist()

    # Load pcd
    pcd = laspy.read(os.path.join(pcd_root, id + '.laz'))

    return wall, roof, floorplan, outline, pcd