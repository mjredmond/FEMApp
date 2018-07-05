from __future__ import print_function, absolute_import

import numpy as np
import vtk
from six.moves import range

from fem.utilities.debug import debuginfo


def project_cell_from_screen(cell, points, renderer, dist):
    cell_type = cell.GetCellType()

    point_ids = cell.GetPointIds()

    id_count = point_ids.GetNumberOfIds()

    if id_count == 0:
        return None

    if cell_type == 1:
        pos = points.GetPoint(point_ids[0])

        new_pos = project_point_from_screen(pos, renderer, dist)

        new_cell = vtk.vtkVertex


def project_point_from_screen(pos, renderer, dist):
    """

    :param pos: list
    :param renderer: vtk.vtkRenderer
    :param dist: float
    :return: list
    """

    renderer.SetWorldPoint(pos[0], pos[1], pos[2], 1.)
    renderer.WorldToDisplay()
    displayCoords = renderer.GetDisplayPoint()

    renderer.SetDisplayPoint(displayCoords[0], displayCoords[1], dist)
    renderer.DisplayToWorld()

    return renderer.GetWorldPoint()


def world_to_view(pos, renderer):
    """

    :param pos: list
    :param renderer: vtk.vtkRenderer
    :return: list
    """

    renderer.SetWorldPoint(pos[0], pos[1], pos[2], 1.)
    renderer.WorldToView()

    return renderer.GetViewPoint()


def view_to_world(pos, renderer):
    """

    :param pos: list
    :param renderer: vtk.vtkRenderer
    :return: list
    """

    renderer.SetViewPoint(pos)
    renderer.ViewToWorld()

    return renderer.GetWorldPoint()


def display_to_world(pos, renderer, dist):
    """

    :param pos: list
    :param renderer: vtk.vtkRenderer
    :param dist: float
    :return: list
    """

    renderer.SetDisplayPoint(pos[0], pos[1], dist)
    renderer.DisplayToWorld()

    return renderer.GetWorldPoint()


def world_to_display(pos, renderer):
    """

    :param pos: list
    :param renderer: vtk.vtkRenderer
    :param dist: float
    :return: list
    """

    renderer.SetWorldPoint(pos[0], pos[1], pos[2])
    renderer.WorldToDisplay()

    return renderer.GetDisplayPoint()


def picking_ray(pos, renderer):
    """

    :param pos: list
    :param renderer: vtk.vtkRenderer
    :return:
    """

    selectionX = pos[0]
    selectionY = pos[1]
    selectionZ = pos[2]

    # code below is adapted from vtkPicker::Pick to calculate ray end points

    # Initialize picking process
    selection_point = [selectionX, selectionY, selectionZ]

    # Get camera focal point and position. Convert to display (screen)
    # coordinates. We need a depth value for z-buffer.
    camera = renderer.GetActiveCamera()
    cameraPos = camera.GetPosition()
    cameraPos += (1.,)
    cameraFP = camera.GetFocalPoint()
    cameraFP += (1.,)

    renderer.SetWorldPoint(cameraFP[0], cameraFP[1], cameraFP[2], cameraFP[3])
    renderer.WorldToDisplay()
    displayCoords = renderer.GetDisplayPoint()
    selectionZ = displayCoords[2]

    # Convert the selection point into world coordinates.
    renderer.SetDisplayPoint(selectionX, selectionY, selectionZ)
    renderer.DisplayToWorld()
    worldCoords = renderer.GetWorldPoint()

    if worldCoords[3] == 0.:
        debuginfo("Bad homogeneous coordinates")
        return -1

    PickPosition = [0, 0, 0]

    for i in range(3):
        PickPosition[i] = worldCoords[i]/worldCoords[3]

    # Compute the ray endpoints.  The ray is along the line running from
    # the camera position to the selection point, starting where this line
    # intersects the front clipping plane, and terminating where this
    # line intersects the back clipping plane.

    ray = [0, 0, 0]
    cameraDOP = [0, 0, 0]

    magnitude = 0.

    for i in range(3):
        ray[i] = PickPosition[i] - cameraPos[i]
        cameraDOP[i] = cameraFP[i] - cameraPos[i]
        magnitude += cameraDOP[i]**2

    magnitude **= 0.5

    for i in range(3):
        cameraDOP[i] /= magnitude

    dot_product = cameraDOP[0]*ray[0] + cameraDOP[1]*ray[1] + cameraDOP[2]*ray[2]

    if dot_product == 0.:
        debuginfo("Cannot process points")
        return -1

    rayLength = dot_product

    clipRange = camera.GetClippingRange()

    p1World = [0, 0, 0, 0]
    p2World = [0, 0, 0, 0]

    if camera.GetParallelProjection():
        tF = clipRange[0] - rayLength
        tB = clipRange[1] - rayLength
        for i in range(3):
            p1World[i] = PickPosition[i] + tF*cameraDOP[i]
            p2World[i] = PickPosition[i] + tB*cameraDOP[i]
    else:
        tF = clipRange[0]/rayLength
        tB = clipRange[1]/rayLength
        for i in range(3):
            p1World[i] = cameraPos[i] + tF*ray[i]
            p2World[i] = cameraPos[i] + tB*ray[i]

    p1World[3] = p2World[3] = 1.

    return [selection_point, PickPosition, p1World, p2World]


def len_between_points(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    dz = p1[2] - p2[2]

    return (dx**2 + dy**2 + dz**2)**0.5


def vector_between_points(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]

    len = (dx**2 + dy**2 + dz**2)**0.5

    if len == 0:
        return [0, 0, 0]
    else:
        return [dx/len, dy/len, dz/len]


def cross_product(v1, v2):
    v3 = [0, 0, 0]

    v3[0] = v1[1]*v2[2] - v1[2]*v2[1]
    v3[1] = -(v1[0]*v2[2] - v1[2]*v2[0])
    v3[2] = v1[0]*v2[1] - v1[1]*v2[0]

    len = (v3[0]**2 + v3[1]**2 + v3[2]**2)**0.5

    if len == 0:
        return [0, 0, 0]
    else:
        return [v3[0]/len, v3[1]/len, v3[2]/len]


def points_to_poly_data(poly_data, points, cells):

    poly_data = poly_data['poly_data']

    point_list = vtk.vtkPoints()

    for i in range(len(points)):
        point_list.InsertNextPoint(points[i][0], points[i][1], points[i][2])

    cell_array = vtk.vtkCellArray()

    for i in range(len(cells)):
        pts = cells[i]

        if len(pts) == 1:
            cell = vtk.vtkVertex()
            ids = cell.GetPointIds()
            ids.SetId(0, pts[0])
        if len(pts) == 2:
            cell = vtk.vtkLine()
            ids = cell.GetPointIds()
            ids.SetId(0, pts[0])
            ids.SetId(1, pts[1])
        elif len(pts) == 3:
            cell = vtk.vtkTriangle()
            ids = cell.GetPointIds()
            ids.SetId(0, pts[0])
            ids.SetId(1, pts[1])
            ids.SetId(2, pts[2])
        elif len(pts) == 4:
            cell = vtk.vtkQuad()
            ids = cell.GetPointIds()
            ids.SetId(0, pts[0])
            ids.SetId(1, pts[1])
            ids.SetId(2, pts[2])
            ids.SetId(3, pts[3])
        else:
            continue

        cell_array.InsertNextCell(cell)

    poly_data.Reset()

    poly_data.SetPoints(point_list)
    poly_data.SetVerts(cell_array)
    poly_data.SetLines(cell_array)
    poly_data.SetPolys(cell_array)


def create_box_frustum(x0_, y0_, x1_, y1_, renderer):

    if x0_ < x1_:
        x0 = x0_
        x1 = x1_
    else:
        x0 = x1_
        x1 = x0_

    if y0_ < y1_:
        y0 = y0_
        y1 = y1_
    else:
        y0 = y1_
        y1 = y0_

    if x0 == x1:
        x1 += 1.

    if y0 == y1:
        y1 += 1.

    verts = []

    renderer.SetDisplayPoint(x0, y0, 0)
    renderer.DisplayToWorld()
    verts.extend(renderer.GetWorldPoint()[:4])

    renderer.SetDisplayPoint(x0, y0, 1)
    renderer.DisplayToWorld()
    verts.extend(renderer.GetWorldPoint()[:4])

    renderer.SetDisplayPoint(x0, y1, 0)
    renderer.DisplayToWorld()
    verts.extend(renderer.GetWorldPoint()[:4])

    renderer.SetDisplayPoint(x0, y1, 1)
    renderer.DisplayToWorld()
    verts.extend(renderer.GetWorldPoint()[:4])

    renderer.SetDisplayPoint(x1, y0, 0)
    renderer.DisplayToWorld()
    verts.extend(renderer.GetWorldPoint()[:4])

    renderer.SetDisplayPoint(x1, y0, 1)
    renderer.DisplayToWorld()
    verts.extend(renderer.GetWorldPoint()[:4])

    renderer.SetDisplayPoint(x1, y1, 0)
    renderer.DisplayToWorld()
    verts.extend(renderer.GetWorldPoint()[:4])

    renderer.SetDisplayPoint(x1, y1, 1)
    renderer.DisplayToWorld()
    verts.extend(renderer.GetWorldPoint()[:4])

    extract_selected_frustum = vtk.vtkExtractSelectedFrustum()
    extract_selected_frustum.CreateFrustum(verts)

    return extract_selected_frustum.GetFrustum()


def box_frustum_volume(frustum):
    """:type frustum: vtk.vtkPlanes"""

    points_ = frustum.GetPoints()
    normals_ = frustum.GetNormals()

    assert points_.GetNumberOfPoints() == 6

    points = []
    normals = []

    for i in range(6):
        points.append(np.array(points_.GetPoint(i), dtype=np.float64))
        normals.append(np.array(normals_.GetTuple3(i), dtype=np.float64))

    used = []
    pairs = []
    count = 0
    while count < 3:
        for i in range(6):
            if i in used:
                continue
            for j in range(6):
                if i == j or j in used:
                    continue

                if round(abs(np.dot(normals[i], normals[j])), 3) == 1.:
                    pairs.append((i, j))
                    used.append(i)
                    used.append(j)
                    count += 1

    dimensions = [0, 0, 0]

    for i in range(3):
        pair = pairs[i]

        i1 = pair[0]
        i2 = pair[1]

        d = points[i1] - points[i2]

        dimensions[i] = np.dot(d, normals[i1])

    debuginfo(dimensions)

    volume = dimensions[0]*dimensions[1]*dimensions[2]

    debuginfo('volume = ', volume)

    return volume


def calculate_normal_from_points(p1, p2, p3):
    v1 = vector_between_points(p1, p2)
    v2 = vector_between_points(p1, p3)

    return cross_product(v1, v2)


def create_triangle_frustum(wp1, wp2, wp3, renderer):

    camera = renderer.GetActiveCamera()

    renderer.SetWorldPoint(wp1[0], wp1[1], wp1[2], 1)
    renderer.WorldToDisplay()
    dp1 = renderer.GetDisplayPoint()

    renderer.SetWorldPoint(wp2[0], wp2[1], wp2[2], 1)
    renderer.WorldToDisplay()
    dp2 = renderer.GetDisplayPoint()

    renderer.SetWorldPoint(wp3[0], wp3[1], wp3[2], 1)
    renderer.WorldToDisplay()
    dp3 = renderer.GetDisplayPoint()

    renderer.SetDisplayPoint(dp1[0], dp1[1], 0)
    renderer.DisplayToWorld()
    wp1 = renderer.GetWorldPoint()[:4]

    renderer.SetDisplayPoint(dp2[0], dp2[1], 0)
    renderer.DisplayToWorld()
    wp2 = renderer.GetWorldPoint()[:4]

    renderer.SetDisplayPoint(dp3[0], dp3[1], 0)
    renderer.DisplayToWorld()
    wp3 = renderer.GetWorldPoint()[:4]

    renderer.SetDisplayPoint(dp1[0], dp1[1], 1)
    renderer.DisplayToWorld()
    wp1_ = renderer.GetWorldPoint()[:4]

    renderer.SetDisplayPoint(dp2[0], dp2[1], 1)
    renderer.DisplayToWorld()
    wp2_ = renderer.GetWorldPoint()[:4]

    renderer.SetDisplayPoint(dp3[0], dp3[1], 1)
    renderer.DisplayToWorld()
    wp3_ = renderer.GetWorldPoint()[:4]

    normals = vtk.vtkFloatArray()
    normals.SetNumberOfComponents(3)
    normals.SetNumberOfTuples(6)

    points = vtk.vtkPoints()
    points.SetNumberOfPoints(6)

    dp1 = [dp1[0], dp1[1], 0]
    dp2 = [dp2[0], dp2[1], 0]
    dp3 = [dp3[0], dp3[1], 0]

    check = calculate_normal_from_points(dp1, dp2, dp3)

    debuginfo(check)

    if check[2] < 0:
        tmp = wp3
        wp3 = wp2
        wp2 = tmp

        tmp = wp3_
        wp3_ = wp2_
        wp2_ = tmp

    normal1 = calculate_normal_from_points(wp1, wp2, wp3)
    points.SetPoint(0, wp1[:3])
    normals.SetTuple3(0, *normal1)

    normal2 = calculate_normal_from_points(wp1_, wp3_, wp2_)
    points.SetPoint(1, wp1_[:3])
    normals.SetTuple3(1, *normal2)

    normal3 = calculate_normal_from_points(wp1, wp3, wp1_)
    points.SetPoint(2, wp1[:3])
    normals.SetTuple3(2, *normal3)

    normal4 = calculate_normal_from_points(wp1, wp1_, wp2)
    points.SetPoint(3, wp1[:3])
    normals.SetTuple3(3, *normal4)

    normal5 = calculate_normal_from_points(wp2, wp2_, wp3)
    points.SetPoint(4, wp2[:3])
    normals.SetTuple3(4, *normal5)

    points.SetPoint(5, wp2[:3])
    normals.SetTuple3(5, *normal5)

    planes = vtk.vtkPlanes()
    planes.SetNormals(normals)
    planes.SetPoints(points)

    return planes


def get_line_pixels(start, end):
    """Bresenham's Line Algorithm
    Produces a list of tuples from start and end

    >>> points1 = get_line((0, 0), (3, 4))
    >>> points2 = get_line((3, 4), (0, 0))
    >>> assert(set(points1) == set(points2))
    >>> debuginfo(points1)
    [(0, 0), (1, 1), (1, 2), (2, 3), (3, 4)]
    >>> debuginfo(points2)
    [(3, 4), (2, 3), (1, 2), (1, 1), (0, 0)]
    """
    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points


def get_ids_by_type(ugrid, id_array, type_array, value_set):
    assert isinstance(value_set, set)

    id_array = ugrid.GetCellData().GetArray(id_array)
    type_array = ugrid.GetCellData().GetArray(type_array)

    result = vtk.vtkIntArray()

    get_value = type_array.GetValue
    get_id = id_array.GetValue

    for i in range(type_array.GetNumberOfTuples()):
        if get_value(i) in value_set:
            result.InsertNextValue(get_id(i))

    return result
