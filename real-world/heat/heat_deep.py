import timeit
import argparse

from gefest.core.opt.gen_design import design
from cases.heat.configuration_dl import heat_sampler, heat_estimator

"""
Before run this script do not forget to 
!pip install --ignore-installed -r real-world/requirements.txt

This file contains short configurated script for generative design of heat sources
with deep discriminate and generative models
More details see in https://github.com/quickjkee/GEFEST/tree/main/cases/heat

The paper results are contained in results_paper.
In performance.pickle we collect best found average temparature
heat.pdf is best found configuration
"""

parser = argparse.ArgumentParser()
parser.add_argument("--pop_size", type=int, default=1, help='number of individs in population')
parser.add_argument("--n_steps", type=int, default=10000, help='number of generative design steps')
parser.add_argument('--n_polys', type=int, default=5, help='maximum number of polygons in structure')
parser.add_argument('--n_points', type=int, default=15, help='maximum number of points in polygon')
parser.add_argument('--c_rate', type=float, default=0.6, help='crossover rate')
parser.add_argument('--m_rate', type=float, default=0.6, help='mutation rate')
parser.add_argument('--is_closed', type=bool, default=False, help='type of polygon')
parser.add_argument('--path_to_sampler', type=str, default='sampler_model/DL_sampler',
                    help='path to deep learning sampler')
parser.add_argument('--path_to_estimator', type=str, default='estimator_model/effnet_mean',
                    help='path to deep learning estimator')
opt = parser.parse_args()

# ------------
# GEFEST tools configuration
# ------------

# Estimator configuration
estimator = heat_estimator.configurate_estimator(path_to_cnn=opt.path_to_estimator)

# Sampler configuration
sampler = heat_sampler.configurate_sampler(domain=None, path_to_sampler=opt.path_to_sampler)

# In this case we do not use optimizer
optimizer = None

# ------------
# Generative design stage
# ------------

start = timeit.default_timer()
optimized_pop = design(n_steps=opt.n_steps,
                       pop_size=opt.pop_size,
                       estimator=estimator,
                       sampler=sampler,
                       optimizer=optimizer)
spend_time = timeit.default_timer() - start
print(f'spent time {spend_time} sec')
