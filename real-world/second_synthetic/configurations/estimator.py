import numpy as np
from types import SimpleNamespace
from uuid import uuid4

from gefest.core.structure.structure import Structure
from gefest.tools.estimators.estimator import Estimator
from gefest.core.geometry.geometry_2d import Geometry2D
from gefest.core.structure.polygon import Polygon
from gefest.core.structure.point import Point


def create_internal() -> 'Structure':
    X0 = [204.7, 206.9, 149.6, 59, 47.3, 60.2, 139.8, 191, 186, 157.9]
    Y0 = [225.2, 237.5, 264, 228, 200.2, 174.7, 106.4, 145, 155, 142.0]

    r = 80
    arc_angles = np.linspace(0 * np.pi, np.pi / 2, 10)
    X1 = list(r * np.cos(arc_angles) + 78)
    Y1 = list(r * np.sin(arc_angles) + 142)

    X = np.array(X0 + X1 + [X0[0]]) / 2 + 50
    Y = np.array(Y0 + Y1 + [Y0[0]]) / 2 + 150

    struct = Polygon(polygon_id=str(uuid4()),
                     points=[(Point(x, y)) for x, y in zip(X, Y)])

    return struct


true = create_internal()


def configurate_estimator(domain):
    # ------------
    # User-defined estimator
    # it should be created as object with .estimate() method
    # ------------

    def multi_loss(struct: Structure):
        if len(struct.polygons) != 1:
            return 1000

        poly_pred = Geometry2D()._poly_to_geom(struct.polygons[0])
        poly_true = Geometry2D()._poly_to_geom(true)

        d1 = poly_pred.difference(poly_true).length
        d2 = poly_true.difference(poly_pred).length

        if d1 < d2:
            return d2
        else:
            return d1

    estimator = SimpleNamespace()
    estimator.estimate = multi_loss

    # ------------
    # GEFEST estimator
    # ------------

    estimator = Estimator(estimator=estimator)

    return estimator
