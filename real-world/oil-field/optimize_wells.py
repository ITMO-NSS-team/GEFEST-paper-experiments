import sys

import numpy as np

from structures.road import Road
from structures.well import Well, pop_well_generation


class Optimization_alg():
    def __init__(self, field, parameters_for_well, parameters_for_GA, NPV, invalid_points):
        self.field = field
        self.npv_f = NPV

        self.parameters_for_well = parameters_for_well
        self.parameters_for_GA = parameters_for_GA
        self.invalid_points = invalid_points

    def run(self, road_structure=None, init_pop=None):
        pop = self.run_joint_GA(road_structure, init_pop)

        return pop, pop[0]

    def run_joint_GA(self, road_structure=None, init_pop=None):
        self.pop_s_well = None
        if init_pop is None:
            self.pop_s_well = self.parameters_for_GA['population_size_well']
        else:
            self.pop_s_well = len(init_pop)

        self.par_s = int(self.parameters_for_GA['parents_portion'] * self.pop_s_well)

        self.prob_mut = self.parameters_for_GA['mutation_probability']
        self.prob_cross = self.parameters_for_GA['crossover_probability']

        trl = self.pop_s_well * self.parameters_for_GA['elit_ratio']
        if trl < 1 and self.parameters_for_GA['elit_ratio'] > 0:
            self.num_elit = 1
        else:
            self.num_elit = int(trl)

        self.iterate = self.parameters_for_GA['max_num_iteration']

        self.r_mut = self.parameters_for_GA['r_mut']

        self.c_type = self.parameters_for_GA['crossover_type']

        self.values_well = np.zeros(self.pop_s_well)

        pop_wells = None
        if init_pop is None:
            pop_wells = np.array(pop_well_generation(self.pop_s_well, self.field, self.parameters_for_well))
        else:
            pop_wells = np.array(init_pop)

        self.calculating_f(pop_wells, 'well', road_structure)

        pop_wells = pop_wells[self.values_well.argsort()]

        self.values_well = np.sort(self.values_well)

        self.best_value_well = self.values_well[0]
        self.best_var_well = pop_wells[0]

        t = 0
        self.report_values_well = []

        while t < self.iterate:
            pop_wells = self.one_iter_GA_well(np.array(pop_wells), road_structure)

            t += 1

        return pop_wells

    def one_iter_GA_well(self, pop_wells, road_structure):
        pop_wells = pop_wells[self.values_well.argsort()]
        self.values_well = np.sort(self.values_well)

        if np.min(self.values_well) < self.best_value_well:
            self.best_value_well = self.values_well[0]
            self.best_var_well = pop_wells[0]

        self.report_values_well.append(self.values_well[0])

        normobj = np.zeros(self.pop_s_well)
        minobj = self.values_well[0]
        if minobj < 0:
            normobj = self.values_well + abs(minobj)
        else:
            normobj = self.values_well.copy()

        maxnorm = np.amax(normobj)
        normobj = maxnorm - normobj + 1

        sum_normobj = np.sum(normobj)
        prob = np.zeros(self.pop_s_well)
        prob = normobj / sum_normobj
        cumprob = np.cumsum(prob)

        par = []

        for k in range(0, self.num_elit):
            par.append(pop_wells[k].copy())

        for k in range(self.num_elit, self.par_s):
            index = np.searchsorted(cumprob, np.random.random())
            par.append(pop_wells[index].copy())

        par = np.array(par)

        ef_par_list = np.array([False] * self.par_s)
        par_count = 0
        while par_count == 0:
            for k in range(0, self.par_s):
                if np.random.random() <= self.prob_cross:
                    ef_par_list[k] = True
                    par_count += 1

        ef_par = par[ef_par_list].copy()

        # New generation
        pop_wells = []

        for k in range(0, self.par_s):
            pop_wells.append(par[k].copy())

        for _ in range(self.par_s, self.pop_s_well, 2):
            r1 = np.random.randint(0, par_count)
            r2 = np.random.randint(0, par_count)
            pvar1 = ef_par[r1].copy()
            pvar2 = ef_par[r2].copy()

            ch = self.cross_well(pvar1, pvar2, self.c_type)
            ch1 = ch[0].copy()
            ch2 = ch[1].copy()

            ch1 = self.mut_well(ch1)
            ch2 = self.mutmidle_well(ch2, pvar1, pvar2)

            pop_wells.append(ch1)
            pop_wells.append(ch2)

        self.calculating_f(pop_wells, 'well', road_structure)

        return pop_wells

    def one_iter_GA_road(self, pop_roads):
        pop_roads = pop_roads[self.values_road.argsort()]
        self.values_road = np.sort(self.values_road)

        if np.min(self.values_road) < self.best_value_road:
            self.best_value_road = self.values_road[0]
            self.best_var_road = pop_roads[0]

        self.report_values_road.append(self.values_road[0])

        normobj = np.zeros(self.pop_s_road)
        minobj = self.values_road[0]
        if minobj < 0:
            normobj = self.values_road + abs(minobj)
        else:
            normobj = self.values_road.copy()

        maxnorm = np.amax(normobj)
        normobj = maxnorm - normobj + 1

        sum_normobj = np.sum(normobj)
        prob = np.zeros(self.pop_s_road)
        prob = normobj / sum_normobj
        cumprob = np.cumsum(prob)

        par = []

        for k in range(0, self.num_elit):
            par.append(pop_roads[k])

        for k in range(self.num_elit, self.par_s):
            index = np.searchsorted(cumprob, np.random.random())
            par.append(pop_roads[index])

        ef_par_list = np.array([False] * self.par_s)

        par = np.array(par)
        par_count = 0
        while par_count == 0:
            for k in range(0, self.par_s):
                if np.random.random() <= self.prob_cross:
                    ef_par_list[k] = True
                    par_count += 1

        ef_par = par[ef_par_list].copy()

        # New generation
        pop_roads = []

        for k in range(0, self.par_s):
            pop_roads.append(par[k])

        for _ in range(self.par_s, self.pop_s_road, 2):
            r1 = np.random.randint(0, par_count)
            r2 = np.random.randint(0, par_count)
            pvar1 = ef_par[r1]
            pvar2 = ef_par[r2]

            ch = self.cross_road(pvar1, pvar2, self.c_type)
            ch1 = ch[0]
            ch2 = ch[1]

            ch1 = self.mut_road(ch1)
            ch2 = self.mutmidle_road(ch2, pvar1, pvar2)

            pop_roads.append(ch1)
            pop_roads.append(ch2)

        self.calculating_f(pop_roads, 'road')

        return pop_roads

    def cross_well(self, x, y, c_type):
        ofs1 = x.copy()
        ofs2 = y.copy()

        for i in range(len(ofs1)):
            ran = np.random.random()
            if ran < self.prob_cross:
                ofs1[i] = y[i]
                ofs2[i] = x[i]

        return np.array([ofs1, ofs2])

    def cross_road(self, x, y, c_type):
        x_coord = x.coord.copy()
        y_coord = y.coord.copy()
        ofs1 = x.coord.copy()
        ofs2 = y.coord.copy()

        if c_type == 'uniform':

            for i in range(len(ofs1)):
                ran = np.random.random()
                if ran < 0.5:
                    ofs1[i] = y_coord[i]
                    ofs2[i] = x_coord[i]

        return np.array([Road(ofs1), Road(ofs2)])

    def mut_well(self, x):
        for i in range(len(x)):
            mut = x[i].start_end

            for j in range(5):
                ran = np.random.random()

                if ran < self.prob_mut:
                    mut[j] = np.random.randint(self.field.all_bounds[j])
            for k in range(len(self.invalid_points[0])):
                if mut[0] == self.invalid_points[0][k] and mut[1] == self.invalid_points[1][k]:
                    return x

            x[i] = Well((mut[0], mut[1]), (mut[2], mut[3], mut[4]), x[i].r)

        return x

    def mut_road(self, x):
        x_coord = x.coord

        for i in range(len(x_coord)):
            ran = np.random.random()

            if ran < self.prob_mut:
                x_coord[i] = (np.random.randint(self.field.all_bounds[0]), np.random.randint(self.field.all_bounds[1]))

        x = Road(x_coord)

        return x

    def mutmidle_well(self, x, p1, p2):
        for i in range(len(x)):
            mut = x[i].start_end
            p1_start_end = p1[i].start_end
            p2_start_end = p2[i].start_end

            for j in range(5):
                ran = np.random.random()

                if ran < self.prob_mut:
                    if p1_start_end[j] < p2_start_end[j]:
                        mut[j] = np.random.randint(p1_start_end[j], p2_start_end[j] + 1)
                    elif p1_start_end[j] > p2_start_end[j]:
                        mut[j] = np.random.randint(p2_start_end[j], p1_start_end[j] + 1)
                    else:
                        mut[j] = np.random.randint(self.field.all_bounds[j])
            for k in range(len(self.invalid_points[0])):
                if mut[0] == self.invalid_points[0][k] and mut[1] == self.invalid_points[1][k]:
                    return x

            x[i] = Well((mut[0], mut[1]), (mut[2], mut[3], mut[4]), x[i].r)

        return x

    def mutmidle_road(self, x, p1, p2):
        x_coord = x.coord
        p1_coord = p1.coord
        p2_coord = p2.coord

        for i in range(len(x_coord)):
            x_coord_i = [x_coord[i][0], x_coord[i][1]]
            for j in range(2):

                ran = np.random.random()

                if ran < self.prob_mut:
                    if p1_coord[i][j] < p2_coord[i][j]:
                        x_coord_i[j] = np.random.randint(p1_coord[i][j], p2_coord[i][j] + 1)
                    elif p1_coord[i][j] > p2_coord[i][j]:
                        x_coord_i[j] = np.random.randint(p2_coord[i][j], p1_coord[i][j] + 1)
                    else:
                        x_coord_i[j] = np.random.randint(self.field.all_bounds[j])

            x_coord[i] = (x_coord_i[0], x_coord_i[1])

        x = Road(x_coord)

        return x

    def calculating_f(self, pop, mode, road_structure=None):
        if mode == 'well':
            self.values_well = []
            for i in range(len(pop)):
                self.values_well.append(self.npv_f.calculated_NPV(pop[i], road_structure))
            self.values_well = np.array(self.values_well)

    def progress(self, count, total, status=''):
        bar_len = 50
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '|' * filled_len + '_' * (bar_len - filled_len)

        sys.stdout.write('\r%s %s%s %s' % (bar, percents, '%', status))
        sys.stdout.flush()
