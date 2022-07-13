import os
import timeit

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from gefest.core.geometry.geometry_2d import Geometry2D
from gefest.core.opt.optimize import optimize
from gefest.core.opt.result import Result
from gefest.core.opt.setup import Setup
from gefest.core.structure.domain import Domain
from gefest.core.structure.point import Point
from gefest.core.structure.polygon import Polygon
from gefest.core.structure.structure import Structure
from gefest.core.viz.struct_vizualizer import StructVizualizer

"""
This file contains synthetic example for closed polygons, we solve isoperimetric task. The global optimum is circle.
Additionally to loss from isoperimetric task you can add fine for number of polygons,
in this example we find three circles.
"""


# Area to length ratio, circle have maximum among all figures (that`s why it`s our optima)
def area_length_ratio(poly):
    area = geometry.get_square(poly)
    length = geometry.get_length(poly)

    if area == 0:
        return None

    ratio = 1 - 4 * np.pi * area / length ** 2

    return ratio


# Adding fine for structures containing imprecise polygons
def multi_loss(struct: Structure):
    loss = 0

    central_poly = Polygon(points=[Point(0, 0), Point(0, 1), Point(1, 0)])
    center_distance_penalty = \
        sum([domain.geometry.min_distance(poly, central_poly) for poly in struct.polygons])

    if len(struct.polygons) == 0:
        return None

    for poly in struct.polygons:
        quality_of_poly = area_length_ratio(poly)
        if quality_of_poly is None:
            return None
        loss += quality_of_poly
    loss = loss / len(struct.polygons)
    L = loss + center_distance_penalty

    return L


expected_sizes = list(range(100, 5000, 100))

fint = []

num_iters = 10
for expected_size in expected_sizes:
    local_fint = []
    for iter in range(num_iters):
        # Usual GEFEST procedure for initialization domain, geometry (with closed or unclosed polygons) and task_setup
        is_closed = True
        geometry = Geometry2D(is_closed=is_closed)
        domain = Domain(allowed_area=[(0, 0),
                                      (0, expected_size),
                                      (expected_size, expected_size),
                                      (expected_size, 0),
                                      (0, 0)],
                        geometry=geometry,
                        max_poly_num=10,
                        min_poly_num=1,
                        max_points_num=50,
                        min_points_num=4,
                        is_closed=is_closed)

        task_setup = Setup(domain=domain)
        res_id = f'exp4_{expected_size}_{iter}'
        spend_time = 0
        if os.path.exists(f'{res_id}.json'):
            result = Result.load(f'{res_id}.json')
            optimized_structure = result.best_structure
            spend_time = result.metadata['time']
            print(f'{res_id} found.')
        else:
            # Optimizing stage
            start = timeit.default_timer()
            result = optimize(task_setup=task_setup,
                              objective_function=multi_loss,
                              pop_size=100,
                              max_gens=100)
            optimized_structure = result.best_structure
            spend_time = timeit.default_timer() - start
            result.name = res_id
            result.metadata['time'] = spend_time
            result.fitness = multi_loss(optimized_structure)

            result.save(f'{result.name}.json')
            # Visualization optimized structure
            visualiser = StructVizualizer(task_setup.domain)
            plt.figure(figsize=(7, 7))

        info = {'spend_time': spend_time,
                'fitness': multi_loss(optimized_structure),
                'type': 'prediction'}
        # visualiser.plot_structure(optimized_structure, info)

        local_fint.append((info['fitness']))
        # plt.title(f'Expected structures: {expected_poly_num}')
        # plt.show()
    fint.append(local_fint)

print(fint)

plot = sns.boxplot(x=expected_sizes, y=fint)
plt.xlabel('Expected domain size')
plt.xticks(rotation=45)

for ind, label in enumerate(plot.get_xticklabels()):
    if ind % 2 == 0:  # every 10th label is kept
        label.set_visible(True)
    else:
        label.set_visible(False)

plt.ylabel('Error for best structure')
#plt.show()
plt.savefig('./exp_domain_size.pdf', format='pdf',bbox_inches='tight')

