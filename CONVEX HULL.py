import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import System.Guid
import math
import Rhino


def calculate_angle(p1, p2):
    x_diff = p2[0] - p1[0]
    y_diff = p2[1] - p1[1]
    return math.atan2(y_diff, x_diff)


def cross_product(a, b):
    lena = math.sqrt(a[0]**2 + a[1]**2)
    lenb = math.sqrt(b[0]**2 + b[1]**2)
    div=lena*lenb
    if div==0:
        return 0
    result = math.degrees(math.asin((a[0] * b[1] - a[1] * b[0])/(div)))
    return result

def cw_turn(p1, p2, p3):
    v1 = (p2[0] - p1[0], p2[1] - p1[1])
    v2 = (p3[0] - p2[0], p3[1] - p2[1])
    cp = cross_product(v1, v2)
    print(cp)
    # if angle between vectors is smaller then 0, this is a ccw turn
    if cp > 0:
        return False
    else:
        return True


# Creates an empty list to hold the points
base_points = []

# Prompt the user to select the points
objs = rs.GetObjects("Select point objects to create the Convex Hull. Press enter when done.", filter=1, preselect=True)

# Appends selected points to the list
for obj in objs:
    #Checks if the object is not a point
    obj_type = rs.ObjectType(obj)
    if obj_type != 1:
        continue
    #Appends points to the list
    else :
        point_obj = rs.PointCoordinates(obj)
        point_tuple = (point_obj[0], point_obj[1])
        base_points.append(point_tuple)

#Initializes the first point list
first_point = []

#Figures out which points from base_points have the lowest x value
#We will start the convex hull from this point, since it's guaranteed to be on the hull

#Initializes a variable to figure out the smallest y value
min_y = float('inf')

#Loops through all the points and writes the one with the smallest y in the first_point variable
for point in base_points:
    if point[1] <= min_y:
        min_y = point[1]
        first_point = [point]

#Initializes the angles list
angles = []


#Stores the tuple (the point and the angle between each point, first_point and the horizontal) in the angles list, using imported calculate_angle function
for point in base_points:
    if point == first_point:
        continue # skip the first point
    angle = calculate_angle(first_point[0], point)
    angles.append((point, angle))

#Sorts the angles list by the second item in each of its tuples, which is the angle between each point, first_point and the horizontal, and stores the first item, which is the point in the new sorted list
#lambda creates an inline funciton that returns the first item of the input list's tuples
sorted_list = [p[0] for p in sorted(angles, key=lambda x: x[1])]


#Appends the first point t the end of the sorted list
sorted_list.append(first_point[0])


#Initializes the convex hull list
convex_hull = []

#Appends the first point in the convex_hull list
convex_hull.append(first_point[0])

#Performs the graham scan algorithm
#Loops through every point in the sorted_list.
#if it detects that the current point forms a clockwise turn in relation to the last two points of the convex_hull list, it will pop the convex_hull list until its length falls below 2 or the evaluated turn becomes counter clockwise
for point in sorted_list:
    while len(convex_hull) >= 2 and cw_turn(convex_hull[-2], convex_hull[-1], point):
            convex_hull.pop()
    convex_hull.append(point)


# Convert tuples to Point3d objects
convex_hull_point3d = [rg.Point3d(point[0], point[1], 0.0) for point in convex_hull]

# Create polyline from points
polyline = rg.Polyline(convex_hull_point3d)

# Add polyline to Rhino document
doc = Rhino.RhinoDoc.ActiveDoc
obj_attributes = doc.CreateDefaultAttributes()
doc.Objects.AddPolyline(polyline, obj_attributes)

# Redraw the viewport to show the new polyline
Rhino.RhinoDoc.ActiveDoc.Views.Redraw()
