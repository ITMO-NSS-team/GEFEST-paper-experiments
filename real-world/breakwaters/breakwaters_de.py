import timeit
import argparse

from gefest.core.opt.gen_design import design
from cases.breakwaters.configuration_de import bw_domain, bw_sampler, bw_estimator, bw_optimizer

"""
Before run this script do not forget to 
!pip install --ignore-installed -r real-world/requirements.txt

This file contains short configurated script for generative design of breakwaters with Differential Evolution
More details see in https://github.com/quickjkee/GEFEST/tree/main/cases/breakwaters

The paper results are contained in /result_paper/BW_DE_60_epochs_30_pop_1(2,3)
To open it use pickle library. There is two types of files
(population_i.pickle and performance_i.pickle). Population contains
coordinates of polygons, performance contains corresponding fitness function.
"""

parser = argparse.ArgumentParser()
parser.add_argument("--pop_size", type=int, default=30, help='number of individs in population')
parser.add_argument("--n_steps", type=int, default=80, help='number of generative design steps')
parser.add_argument('--n_polys', type=int, default=5, help='maximum number of polygons in structure')
parser.add_argument('--n_points', type=int, default=15, help='maximum number of points in polygon')
parser.add_argument('--c_rate', type=float, default=0.6, help='crossover rate')
parser.add_argument('--m_rate', type=float, default=0.6, help='mutation rate')
parser.add_argument('--is_closed', type=bool, default=False, help='type of polygon')
parser.add_argument('--path_to_sim', type=str, default='swan_model/', help='path to physical simulator')
opt = parser.parse_args()

# ------------
# GEFEST tools configuration
# ------------

# Domain configuration
domain, task_setup = bw_domain.configurate_domain(poly_num=opt.n_polys,
                                                  points_num=opt.n_points,
                                                  is_closed=opt.is_closed)

# Estimator configuration
estimator = bw_estimator.configurate_estimator(domain=domain,
                                               path_sim=opt.path_to_sim)

# Sampler configuration
sampler = bw_sampler.configurate_sampler(domain=domain)

# Optimizer configuration
optimizer = bw_optimizer.configurate_optimizer(pop_size=opt.pop_size,
                                               crossover_rate=opt.c_rate,
                                               mutation_rate=opt.m_rate,
                                               task_setup=task_setup)

# ------------
# Generative design stage
# ------------

start = timeit.default_timer()
optimized_pop = design(n_steps=opt.n_steps,
                       pop_size=opt.pop_size,
                       estimator=estimator,
                       sampler=sampler,
                       optimizer=optimizer,
                       extra=True)
spend_time = timeit.default_timer() - start
print(f'spent time {spend_time} sec')
