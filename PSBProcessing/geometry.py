# Reference from https://www.oreilly.com/ideas/an-elegant-solution-to-the-convex-hull-problem
import numpy as np
import math


def split(u, v, points):
    # return points on left side of UV
    return [p for p in points if np.cross(p - u, v - u) < 0]


def extend(u, v, points):
    if not points:
        return []

    # find furthest point W, and split search to WV, UW
    w = min(points, key=lambda p: np.cross(p - u, v - u))
    p1, p2 = split(w, v, points), split(u, w, points)
    return extend(w, v, p1) + [w] + extend(u, w, p2)


def convex_hull(points):
    # find two hull points, U, V, and split to left and right search
    u = min(points, key=lambda p: p[0])
    v = max(points, key=lambda p: p[0])
    left, right = split(u, v, points), split(v, u, points)

    # find convex hull on each side
    return np.array([v] + extend(u, v, left) + [u] + extend(v, u, right) + [v])


def poly_area(pts):
    lines = np.hstack([pts, np.roll(pts, -1, axis=0)])
    area = 0.5 * abs(sum(x1 * y2 - x2 * y1 for x1, y1, x2, y2 in lines))
    return area


def min_bounding_rect(hull_points_2d):
    # Compute edges (x2-x1,y2-y1)
    edges = np.zeros((len(hull_points_2d) - 1, 2))  # empty 2 column array
    for i in range(len(edges)):
        edge_x = hull_points_2d[i + 1, 0] - hull_points_2d[i, 0]
        edge_y = hull_points_2d[i + 1, 1] - hull_points_2d[i, 1]
        edges[i] = [edge_x, edge_y]
    #print "Edges: \n", edges

    # Calculate edge angles   atan2(y/x)
    edge_angles = np.zeros((len(edges)))  # empty 1 column array
    for i in range(len(edge_angles)):
        edge_angles[i] = math.atan2(edges[i, 1], edges[i, 0])
    #print "Edge angles: \n", edge_angles

    # Check for angles in 1st quadrant
    for i in range(len(edge_angles)):
        edge_angles[i] = abs(edge_angles[i] %
                             (math.pi / 2))  # want strictly positive answers
    #print "Edge angles in 1st Quadrant: \n", edge_angles

    # Remove duplicate angles
    edge_angles = np.unique(edge_angles)
    #print "Unique edge angles: \n", edge_angles

    # Test each angle to find bounding box with smallest area
    min_bbox = (0, np.iinfo(0).max, 0, 0, 0, 0, 0, 0
                )  # rot_angle, area, width, height, min_x, max_x, min_y, max_y
    # print "Testing", len(edge_angles), "possible rotations for bounding box... \n"
    for i in range(len(edge_angles)):

        # Create rotation matrix to shift points to baseline
        # R = [ cos(theta)      , cos(theta-PI/2)
        #       cos(theta+PI/2) , cos(theta)     ]
        R = np.array([[
            math.cos(edge_angles[i]),
            math.cos(edge_angles[i] - (math.pi / 2))
        ], [
            math.cos(edge_angles[i] + (math.pi / 2)),
            math.cos(edge_angles[i])
        ]])
        #print "Rotation matrix for ", edge_angles[i], " is \n", R

        # Apply this rotation to convex hull points
        rot_points = np.dot(R, np.transpose(hull_points_2d))  # 2x2 * 2xn
        #print "Rotated hull points are \n", rot_points

        # Find min/max x,y points
        min_x = np.nanmin(rot_points[0], axis=0)
        max_x = np.nanmax(rot_points[0], axis=0)
        min_y = np.nanmin(rot_points[1], axis=0)
        max_y = np.nanmax(rot_points[1], axis=0)
        #print "Min x:", min_x, " Max x: ", max_x, "   Min y:", min_y, " Max y: ", max_y

        # Calculate height/width/area of this bounding rectangle
        width = max_x - min_x
        height = max_y - min_y
        area = width * height
        #print "Potential bounding box ", i, ":  width: ", width, " height: ", height, "  area: ", area

        # Store the smallest rect found first (a simple convex hull might have 2 answers with same area)
        if (area < min_bbox[1]):
            min_bbox = (edge_angles[i], area, width, height, min_x, max_x,
                        min_y, max_y)
        # Bypass, return the last found rect
        #min_bbox = ( edge_angles[i], area, width, height, min_x, max_x, min_y, max_y )

    # Re-create rotation matrix for smallest rect
    angle = min_bbox[0]
    R = np.array([[math.cos(angle),
                   math.cos(angle - (math.pi / 2))],
                  [math.cos(angle + (math.pi / 2)),
                   math.cos(angle)]])
    #print "Projection matrix: \n", R

    # Project convex hull points onto rotated frame
    proj_points = np.dot(R, np.transpose(hull_points_2d))  # 2x2 * 2xn
    #print "Project hull points are \n", proj_points

    # min/max x,y points are against baseline
    min_x = min_bbox[4]
    max_x = min_bbox[5]
    min_y = min_bbox[6]
    max_y = min_bbox[7]
    #print "Min x:", min_x, " Max x: ", max_x, "   Min y:", min_y, " Max y: ", max_y

    # Calculate center point and project onto rotated frame
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    center_point = np.dot([center_x, center_y], R)
    #print "Bounding box center point: \n", center_point

    # Calculate corner points and project onto rotated frame
    corner_points = np.zeros((4, 2))  # empty 2 column array
    corner_points[0] = np.dot([max_x, min_y], R)
    corner_points[1] = np.dot([min_x, min_y], R)
    corner_points[2] = np.dot([min_x, max_y], R)
    corner_points[3] = np.dot([max_x, max_y], R)
    #print "Bounding box corner points: \n", corner_points

    #print "Angle of rotation: ", angle, "rad  ", angle * (180/math.pi), "deg"

    return corner_points


def score_profile(profile):
    hull = convex_hull(profile)
    rect = min_bounding_rect(hull)
    return len(hull), 1 - poly_area(hull) / poly_area(rect)
