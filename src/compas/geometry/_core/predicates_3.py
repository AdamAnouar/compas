from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.utilities import window

from compas.geometry import subtract_vectors
from compas.geometry import cross_vectors
from compas.geometry import dot_vectors
from compas.geometry import centroid_points
from compas.geometry import normal_polygon
from compas.geometry import length_vector_sqrd

from compas.geometry import distance_point_point
from compas.geometry import distance_point_plane
from compas.geometry import distance_point_line
from compas.geometry import closest_point_on_segment


# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# Colinear, Coplanar
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================


def is_colinear(a, b, c, tol=1e-6):
    """Determine if three points are colinear.

    Parameters
    ----------
    a : [float, float, float] | :class:`compas.geometry.Point`
        Point 1.
    b : [float, float, float] | :class:`compas.geometry.Point`
        Point 2.
    c : [float, float, float] | :class:`compas.geometry.Point`
        Point 3.
    tol : float, optional
        Tolerance for comparing the area of the triangle defined by the three points with zero.

    Returns
    -------
    bool
        True if the points are colinear.
        False otherwise.

    See Also
    --------
    is_colinear_line_line
    is_coplanar

    """
    return 0.5 * length_vector_sqrd(cross_vectors(subtract_vectors(b, a), subtract_vectors(c, a))) < tol**2


def is_colinear_line_line(line1, line2, tol=1e-6):
    """Determine if two lines are colinear.

    Parameters
    ----------
    line1 : [point, point] | :class:`compas.geometry.Line`
        Line 1.
    line2 : [point, point] | :class:`compas.geometry.Line`
        Line 2.
    tol : float, optional
        A tolerance for colinearity verification.

    Returns
    -------
    bool
        True if the lines are colinear.
        False otherwise.

    See Also
    --------
    is_colinear
    is_coplanar

    """
    a, b = line1
    c, d = line2
    return is_colinear(a, b, c, tol) and is_colinear(a, b, d, tol)


def is_coplanar(points, tol=1e-6):
    """Determine if the points are coplanar.

    Parameters
    ----------
    points : sequence[point]
        A sequence of point locations.
    tol : float, optional
        A tolerance for planarity validation.

    Returns
    -------
    bool
        True if the points are coplanar.
        False otherwise.

    See Also
    --------
    is_colinear
    is_colinear_line_line

    Notes
    -----
    Compute the normal vector (cross product) of the vectors formed by the first three points.
    Taking the first point as base point, include one more vector at a time and check if that vector is perpendicular to the normal vector.
    If all vectors are perpendicular, the points are coplanar.

    """
    if len(points) < 4:
        return True

    tol2 = tol**2
    temp = points[:]

    while True:
        a = temp.pop(0)
        b = temp.pop(0)
        c = temp.pop(0)
        n = cross_vectors(subtract_vectors(b, a), subtract_vectors(c, a))
        if not (0.5 * length_vector_sqrd(n) < tol2):
            # perhaps we should use a different tolerance here?
            # or rather check if the squared length is large enough?
            break
        if not temp:
            return True

    return all(is_perpendicular_vector_vector(n, subtract_vectors(d, a), tol) for d in temp)


# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# Parallel, Perpendicular
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================


def is_parallel_vector_vector(u, v, tol=1e-6):
    """Determine if two vectors are parallel.

    Parameters
    ----------
    u : [float, float, float] | :class:`compas.geometry.Vector`
        Vector 1.
    v : [float, float, float] | :class:`compas.geometry.Vector`
        Vector 2.
    tol : float, optional
        A tolerance for comparing the length of the cross product to zero.

    Returns
    -------
    bool
        True if the vectors are parallel.
        False otherwise.

    See Also
    --------
    is_parallel_line_line
    is_parallel_plane_plane
    is_perpendicular_vector_vector

    Notes
    -----
    This function does not distinguish between parallel and antiparallel vectors.

    """
    # uv = dot_vectors(u, v)
    # uu = dot_vectors(u, u)
    # vv = dot_vectors(v, v)
    # return abs(uv * uv - uu * vv) < tol
    u_v = cross_vectors(u, v)
    return dot_vectors(u_v, u_v) < tol**2
    # return abs(dot_vectors(normalize_vector(u), normalize_vector(v)) - 1.0) < tol


def is_parallel_line_line(line1, line2, tol=1e-6):
    """Determine if two lines are parallel.

    Parameters
    ----------
    line1 : [point, point] | :class:`compas.geometry.Line`
        Line 1.
    line2 : [point, point] | :class:`compas.geometry.Line`
        Line 2.
    tol : float, optional
        A tolerance for verifying parallelity of the line direction vectors.

    Returns
    -------
    bool
        True if the lines are colinear.
        False otherwise.

    See Also
    --------
    is_parallel_vector_vector
    is_parallel_plane_plane
    is_perpendicular_line_line

    """
    a, b = line1
    c, d = line2
    # e1 = normalize_vector(subtract_vectors(b, a))
    # e2 = normalize_vector(subtract_vectors(d, c))
    # return abs(dot_vectors(e1, e2)) > 1.0 - tol
    return is_parallel_vector_vector(subtract_vectors(b, a), subtract_vectors(d, c), tol)


def is_parallel_plane_plane(plane1, plane2, tol=1e-6):
    """Determine if two planes are parallel.

    Parameters
    ----------
    plane1 : [point, vector] | :class:`compas.geometry.Plane`
        Plane 1.
    plane2 : [point, vector] | :class:`compas.geometry.Plane`
        Plane 2.
    tol : float, optional
        A tolerance for verifying parallelity of the plane normals.

    Returns
    -------
    bool
        True if the planes are parallel.
        False otherwise.

    See Also
    --------
    is_parallel_vector_vector
    is_parallel_line_line
    is_perpendicular_plane_plane

    """
    return is_parallel_vector_vector(plane1[1], plane2[1], tol)


def is_perpendicular_vector_vector(u, v, tol=1e-6):
    """Determine if two vectors are perpendicular.

    Parameters
    ----------
    u : [float, float, float] | :class:`compas.geometry.Vector`
        Vector 1.
    v : [float, float, float] | :class:`compas.geometry.Vector`
        Vector 2.
    tol : float, optional
        A tolerance for comparing the dot product of the two vectors to zero.

    Returns
    -------
    bool
        True if the vectors are perpendicular.
        False otherwise.

    See Also
    --------
    is_perpendicular_line_line
    is_perpendicular_plane_plane
    is_parallel_vector_vector

    """
    return abs(dot_vectors(u, v)) < tol


def is_perpendicular_line_line(line1, line2, tol=1e-6):
    """Determine if two lines are perpendicular.

    Parameters
    ----------
    line1 : [point, point] | :class:`compas.geometry.Line`
        Line 1.
    line2 : [point, point] | :class:`compas.geometry.Line`
        Line 2.
    tol : float, optional
        A tolerance for verifying perpendicularity of the line direction vectors.

    Returns
    -------
    bool
        True if the lines are perpendicular.
        False otherwise.

    See Also
    --------
    is_perpendicular_vector_vector
    is_perpendicular_plane_plane
    is_parallel_line_line

    """
    return is_perpendicular_vector_vector(
        subtract_vectors(line1[1], line1[0]),
        subtract_vectors(line2[1], line2[0]),
        tol,
    )


def is_perpendicular_plane_plane(plane1, plane2, tol=1e-6):
    """Determine if two planes are perpendicular.

    Parameters
    ----------
    plane1 : [point, vector] | :class:`compas.geometry.Plane`
        Plane 1.
    plane2 : [point, vector] | :class:`compas.geometry.Plane`
        Plane 2.
    tol : float, optional
        A tolerance for verifying perpendicularity of the plane normals.

    Returns
    -------
    bool
        True if the planes are perpendicular.
        False otherwise.

    See Also
    --------
    is_perpendicular_vector_vector
    is_perpendicular_line_line
    is_parallel_plane_plane

    """
    return is_perpendicular_vector_vector(plane1[1], plane2[1], tol)


# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# Convexity
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================


def is_polygon_convex(polygon):
    """Determine if a polygon is convex.

    Parameters
    ----------
    polygon : sequence[point] | :class:`compas.geometry.Polygon`
        A polygon.

    Returns
    -------
    bool
        True if the polygon is convex.
        False otherwise.

    See Also
    --------
    is_polyhedron_convex

    Notes
    -----
    Use this function for *spatial* polygons.
    If the polygon is in a horizontal plane, use :func:`is_polygon_convex_xy` instead.

    Examples
    --------
    >>> polygon = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.4, 0.4, 0.0], [0.0, 1.0, 0.0]]
    >>> is_polygon_convex(polygon)
    False

    """
    a = polygon[0]
    o = polygon[1]
    b = polygon[2]
    oa = subtract_vectors(a, o)
    ob = subtract_vectors(b, o)
    n0 = cross_vectors(oa, ob)
    for a, o, b in window(polygon + polygon[:2], 3):
        oa = subtract_vectors(a, o)
        ob = subtract_vectors(b, o)
        n = cross_vectors(oa, ob)
        if dot_vectors(n, n0) >= 0:
            continue
        else:
            return False
    return True


def is_polyhedron_convex(polyhedron):
    """Determine if a polyhedron is convex.

    Parameters
    ----------
    polyhedron : [sequence[point], sequence[sequence[int]]] | :class:`compas.geometry.Polyhedron`
        A polyhedron defined by a sequence of points
        and a sequence of faces, with each face defined as a sequence of indices into the sequence of points.

    Returns
    -------
    bool
        True if the polyhedron is convex.
        False otherwise.

    See Also
    --------
    is_polygon_convex

    """
    vertices, faces = polyhedron
    for face in faces:
        base = vertices[face[0]]
        normal = normal_polygon([vertices[index] for index in face])
        direction = None
        for i in range(len(vertices)):
            if i not in face:
                point = vertices[i]
                if direction is None:
                    direction = dot_vectors(subtract_vectors(point, base), normal) >= 0
                else:
                    if dot_vectors(subtract_vectors(point, base), normal) >= 0 != direction:
                        return False
    return True


# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# Containment (Plane)
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================


def is_point_on_plane(point, plane, tol=1e-6):
    """Determine if a point lies on a plane.

    Parameters
    ----------
    point : [float, float, float] | :class:`compas.geometry.Point`
        A point.
    plane : [point, vector] | :class:`compas.geometry.Plane`
        A plane.
    tol : float, optional
        A tolerance for membership verification.

    Returns
    -------
    bool
        True if the point is in on the plane.
        False otherwise.

    """
    return distance_point_plane(point, plane) <= tol


# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# Containment (Curves)
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================


def is_point_on_line(point, line, tol=1e-6):
    """Determine if a point lies on a line.

    Parameters
    ----------
    point : [float, float, float] | :class:`compas.geometry.Point`
        A point.
    line : [point, point] | :class:`compas.geometry.Line`
        A line.
    tol : float, optional
        A tolerance for membership verification.

    Returns
    -------
    bool
        True if the point is in on the line.
        False otherwise.

    """
    return distance_point_line(point, line) <= tol


def is_point_on_segment(point, segment, tol=1e-6):
    """Determine if a point lies on a given line segment.

    Parameters
    ----------
    point : [float, float, float] | :class:`compas.geometry.Point`
        A point.
    segment : [point, point] | :class:`compas.geometry.Line`
        A line segment.
    tol : float, optional
        A tolerance for membership verification.

    Returns
    -------
    bool
        True if the point is on the line segment.
        False otherwise.

    """
    a, b = segment

    d_ab = distance_point_point(a, b)
    if d_ab == 0:
        return False

    if not is_point_on_line(point, (a, b), tol=tol):
        return False

    d_pa = distance_point_point(a, point)
    d_pb = distance_point_point(b, point)

    if d_pa + d_pb <= d_ab + tol:
        return True
    return False


def is_point_on_polyline(point, polyline, tol=1e-6):
    """Determine if a point is on a polyline.

    Parameters
    ----------
    point : [float, float, float] | :class:`compas.geometry.Point`
        A point.
    polyline : sequence[point] | :class:`compas.geometry.Polyline`
        A polyline.
    tol : float, optional
        The tolerance for membership verification.

    Returns
    -------
    bool
        True if the point is on the polyline.
        False otherwise.

    """
    for i in range(len(polyline) - 1):
        a = polyline[i]
        b = polyline[i + 1]
        c = closest_point_on_segment(point, (a, b))

        if distance_point_point(point, c) <= tol:
            return True

    return False


def is_point_on_circle(point, circle, tol=1e-6):
    """Determine if a point lies on a circle.

    Parameters
    ----------
    point : [float, float, float] | :class:`compas.geometry.Point`
        A point.
    circle : [plane, float]
        A circle.
    tol : float, optional
        A tolerance for membership verification.

    Returns
    -------
    bool
        True if the point lies on the circle.
        False otherwise.

    """
    plane, radius = circle
    if is_point_on_plane(point, plane):
        return abs(distance_point_point(point, plane[0]) - radius) <= tol
    return False


# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# Containment (Surfaces)
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================


# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# Containment (Shapes)
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================


def is_point_in_circle(point, circle, tol=1e-6):
    """Determine if a point lies in a circle.

    Parameters
    ----------
    point : [float, float, float] | :class:`compas.geometry.Point`
        A point.
    circle : [plane, float]
        A circle.

    Returns
    -------
    bool
        True if the point lies in the circle.
        False otherwise.

    """
    plane, radius = circle
    if is_point_on_plane(point, plane, tol=tol):
        return distance_point_point(point, plane[0]) <= radius
    return False


def is_point_in_triangle(point, triangle, tol=1e-6):
    """Determine if a point is in the interior of a triangle.

    Parameters
    ----------
    point : [float, float, float] | :class:`compas.geometry.Point`
        A point.
    triangle : [point, point, point]
        A triangle.

    Returns
    -------
    bool
        True if the point is in inside the triangle.
        False otherwise.

    See Also
    --------
    compas.geometry.is_point_in_triangle_xy

    """

    def is_on_same_side(p1, p2, segment):
        a, b = segment
        v = subtract_vectors(b, a)
        c1 = cross_vectors(v, subtract_vectors(p1, a))
        c2 = cross_vectors(v, subtract_vectors(p2, a))
        if dot_vectors(c1, c2) >= 0:
            return True
        return False

    a, b, c = triangle

    if is_point_on_plane(point, (a, normal_polygon(triangle)), tol=tol):
        if (
            is_on_same_side(point, a, (b, c))
            and is_on_same_side(point, b, (a, c))
            and is_on_same_side(point, c, (a, b))
        ):
            return True

    return False


def is_point_in_polygon(point, polygon, tol=1e-6):
    """Determine if a point is in the interior of a polygon.

    Parameters
    ----------
    point : [float, float, float] | :class:`compas.geometry.Point`
        A point.
    polygon : sequence[point] | :class:`compas.geometry.Polygon`
        A polygon.

    Returns
    -------
    bool
        True if the point is in inside the polygon.
        False otherwise.

    """
    raise NotImplementedError


# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# Containment (Solids)
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================


def is_point_in_sphere(point, sphere, tol=1e-6):
    """Determine if a point lies in a sphere.

    Parameters
    ----------
    point : [float, float, float] | :class:`compas.geometry.Point`
        A point.
    sphere : [point, float]
        A sphere.

    Returns
    -------
    bool
        True if the point lies in the sphere.
        False otherwise.

    """
    center, radius = sphere
    return distance_point_point(point, center) <= radius + tol


def is_point_in_aab(point, box, tol=1e-6):
    """Determine if a point lies in an axis-aligned box.

    Parameters
    ----------
    point : [float, float, float] | :class:`compas.geometry.Point`
        A point.
    box : [[float, float, float], [float, float, float]] | [:class:`compas.geometry.Point`, :class:`compas.geometry.Point``]
        An axis-aligned box defined by the min/max corners.

    Returns
    -------
    bool
        True if the point lies in the box.
        False otherwise.

    """
    a, b = box
    return all(a[i] - tol <= point[i] <= b[i] + tol for i in range(3))


def is_point_in_polyhedron(point, polyhedron):
    """Determine if the point lies inside the given polyhedron.

    Parameters
    ----------
    point : [float, float, float] | :class:`compas.geometry.Point`
        The test point.
    polyhedron : [sequence[point], sequence[sequence[int]]] | :class:`compas.geometry.Polyhedron`.
        The polyhedron defined by a sequence of points
        and a sequence of faces, with each face defined as a sequence of indices into the sequence of points.

    Returns
    -------
    bool
        True, if the point lies in the polyhedron.
        False, otherwise.

    """
    vertices, faces = polyhedron
    polygons = [[vertices[index] for index in face] for face in faces]
    planes = [[centroid_points(polygon), normal_polygon(polygon)] for polygon in polygons]
    return all(is_point_behind_plane(point, plane) for plane in planes)


def is_point_infront_plane(point, plane, tol=1e-6):
    """Determine if a point lies in front of a plane.

    Parameters
    ----------
    point : [float, float, float] | :class:`compas.geometry.Point`
        A point.
    plane : [point, vector] | :class:`compas.geometry.Plane`
        A plane.
    tol : float, optional
        A tolerance for membership verification.

    Returns
    -------
    bool
        True if the point is in front of the plane.
        False otherwise.

    """
    return dot_vectors(subtract_vectors(point, plane[0]), plane[1]) > tol


def is_point_behind_plane(point, plane, tol=1e-6):
    """Determine if a point lies behind a plane.

    Parameters
    ----------
    point : [float, float, float] | :class:`compas.geometry.Point`
        A point.
    plane : [point,  normal] | :class:`compas.geometry.Plane`
        A plane.
    tol : float, optional
        A tolerance for membership verification.

    Returns
    -------
    bool
        True if the point is in front of the plane.
        False otherwise.

    """
    return dot_vectors(subtract_vectors(point, plane[0]), plane[1]) < -tol


# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# Deprecated
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================


# def is_intersection_line_line(l1, l2, tol=1e-6):
#     """Verifies if two lines intersect.

#     Parameters
#     ----------
#     l1 : [point, point] | :class:`compas.geometry.Line`
#         A line.
#     l2 : [point, point] | :class:`compas.geometry.Line`
#         A line.
#     tol : float, optional
#         A tolerance for intersection verification.

#     Returns
#     -------
#     bool
#         True if the lines intersect in one point.
#         False if the lines are skew, parallel or lie on top of each other.

#     """
#     a, b = l1
#     c, d = l2

#     e1 = normalize_vector(subtract_vectors(b, a))
#     e2 = normalize_vector(subtract_vectors(d, c))

#     # check for parallel lines
#     if abs(dot_vectors(e1, e2)) > 1.0 - tol:
#         return False

#     # check for intersection
#     if abs(dot_vectors(cross_vectors(e1, e2), subtract_vectors(c, a))) < tol:
#         return True
#     return False


# def is_intersection_segment_segment(s1, s2, tol=1e-6):
#     """Verifies if two segments intersect.

#     Parameters
#     ----------
#     s1 : [point, point] | :class:`compas.geometry.Line`
#         A line segment.
#     s2 : [point, point] | :class:`compas.geometry.Line`
#         A line segment.
#     tol : float, optional
#         A tolerance for intersection verification.

#     Returns
#     -------
#     bool
#         True if the segments intersect in one point.
#         False if the segments are skew, parallel or lie on top of each other.

#     """
#     raise NotImplementedError


# def is_intersection_line_triangle(line, triangle, tol=1e-6):
#     """Verifies if a line (ray) intersects with a triangle.

#     Parameters
#     ----------
#     line : [point, point] | :class:`compas.geometry.Line`
#         A line.
#     triangle : [point, point, point]
#         A triangle.
#     tol : float, optional
#         A tolerance for intersection verification.

#     Returns
#     -------
#     bool
#         True if the line (ray) intersects with the triangle.
#         False otherwise.

#     Notes
#     -----
#     Based on the Moeller Trumbore intersection algorithm.
#     The line is treated as continues, directed ray and not as line segment with a start and end point

#     Examples
#     --------
#     >>>

#     """
#     a, b, c = triangle
#     # direction vector and base point of line
#     v1 = subtract_vectors(line[1], line[0])
#     p1 = line[0]
#     # Find vectors for two edges sharing triangle vertex 1
#     e1 = subtract_vectors(b, a)
#     e2 = subtract_vectors(c, a)
#     # Begin calculating determinant - also used to calculate u parameter
#     p = cross_vectors(v1, e2)
#     # if determinant is near zero, ray lies in plane of triangle
#     det = dot_vectors(e1, p)

#     # NOT CULLING
#     if det > -tol and det < tol:
#         return False

#     inv_det = 1.0 / det
#     # calculate distance from V1 to ray origin
#     t = subtract_vectors(p1, a)
#     # Calculate u parameter and make_blocks bound
#     u = dot_vectors(t, p) * inv_det

#     # The intersection lies outside of the triangle
#     if u < 0.0 or u > 1.0:
#         return False

#     # Prepare to make_blocks v parameter
#     q = cross_vectors(t, e1)
#     # Calculate V parameter and make_blocks bound
#     v = dot_vectors(v1, q) * inv_det

#     # The intersection lies outside of the triangle
#     if v < 0.0 or u + v > 1.0:
#         return False

#     t = dot_vectors(e2, q) * inv_det

#     if t > tol:
#         return True
#     # No hit
#     return False


# def is_intersection_line_plane(line, plane, tol=1e-6):
#     """Determine if a line (ray) intersects with a plane.

#     Parameters
#     ----------
#     line : [point, point] | :class:`compas.geometry.Line`
#         A line.
#     plane : [point, vector] | :class:`compas.geometry.Plane`
#         A plane.
#     tol : float, optional
#         A tolerance for intersection verification.

#     Returns
#     -------
#     bool
#         True if the line intersects with the plane.
#         False otherwise.

#     """
#     pt1 = line[0]
#     pt2 = line[1]
#     p_norm = plane[1]

#     v1 = subtract_vectors(pt2, pt1)
#     dot = dot_vectors(p_norm, v1)

#     if fabs(dot) > tol:
#         return True
#     return False


# def is_intersection_segment_plane(segment, plane, tol=1e-6):
#     """Determine if a line segment intersects with a plane.

#     Parameters
#     ----------
#     segment : [point, point] | :class:`compas.geometry.Line`
#         A line segment.
#     plane : [point, vector] | :class:`compas.geometry.Plane`
#         A plane.
#     tol : float, optional
#         A tolerance for intersection verification.

#     Returns
#     -------
#     bool
#         True if the segment intersects with the plane.
#         False otherwise.

#     """
#     pt1 = segment[0]
#     pt2 = segment[1]
#     p_cent = plane[0]
#     p_norm = plane[1]

#     v1 = subtract_vectors(pt2, pt1)
#     dot = dot_vectors(p_norm, v1)

#     if fabs(dot) > tol:
#         v2 = subtract_vectors(pt1, p_cent)
#         fac = -dot_vectors(p_norm, v2) / dot
#         if fac > 0.0 and fac < 1.0:
#             return True
#         return False
#     else:
#         return False


# def is_intersection_plane_plane(plane1, plane2, tol=1e-6):
#     """Verifies if two planes intersect.

#     Parameters
#     ----------
#     plane1 : [point, vector] | :class:`compas.geometry.Plane`
#         A plane.
#     plane2 : [point, vector] | :class:`compas.geometry.Plane`
#         A plane.
#     tol : float, optional
#         A tolerance for intersection verification.

#     Returns
#     -------
#     bool
#         True if plane1 intersects with plane2.
#         False otherwise.

#     """
#     # check for parallelity of planes
#     if abs(dot_vectors(plane1[1], plane2[1])) > 1 - tol:
#         return False
#     return True
