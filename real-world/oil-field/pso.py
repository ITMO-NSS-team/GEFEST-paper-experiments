import numpy as np

from structures.well import Well, pop_well_generation, check_correctness_well


class PSO():
    def __init__(self, field, n_particles, parameters_for_well, c0=1.193, c1=1.193, w=0.721, npv=None, pop=None,
                 best=None):
        self.field = field
        self.n_particles = n_particles
        self.particle_dim = 5 * parameters_for_well['count_well']
        self.npv = npv

        self.c0 = c0
        self.c1 = c1
        self.w = w

        self.parameters_for_well = parameters_for_well
        if pop is None:
            self.particles_pos = pop_well_generation(self.n_particles, self.field, self.parameters_for_well)
        else:
            self.particles_pos = pop
            # Initialize particle velocities using a uniform distribution
        self.velocities = np.random.uniform(size=(self.n_particles, self.particle_dim))

        # Initialize the best positions
        if best is not None:
            self.g_best = best
        else:
            self.g_best = self.particles_pos[0]
        self.p_best = self.particles_pos

    def well_operation_coord_w_v(self, well, vector):
        new_wells = []
        for i in range(len(well)):
            new_well = Well((well[i].start[0] + vector[5 * i + 0], well[i].start[1] + vector[5 * i + 1]),
                            (well[i].end[0] + vector[5 * i + 2],
                             well[i].end[1] + vector[5 * i + 3], well[i].end[2] + vector[5 * i + 4]), 2)
            if check_correctness_well(new_well, self.field):
                new_wells += [new_well]
            else:
                new_wells += [well[i]]

        return new_wells

    def well_operation_coord_diff_w(self, well_1, well_2, coeff):
        res = []
        for i, well_1_i in enumerate(well_1):
            res += [(well_1_i.start[0] - well_2[i].start[0]) * coeff, (well_1_i.start[1] - well_2[i].start[1]) * coeff,
                    (well_1_i.end[0] - well_2[i].end[0]) * coeff,
                    (well_1_i.end[1] - well_2[i].end[1]) * coeff, (well_1_i.end[2] - well_2[i].end[2]) * coeff]

        return np.array(res)

    def update_position(self, x, v):
        v = np.array(v)
        new_x = self.well_operation_coord_w_v(x, v)

        return new_x

    def update_velocity(self, x, v, p_best, g_best):
        x = x
        v = np.array(v)
        r = np.random.uniform()
        p_best = p_best
        g_best = g_best

        new_v = self.w * v + self.well_operation_coord_diff_w(p_best, x,
                                                              self.c0 * r) + self.well_operation_coord_diff_w(g_best, x,
                                                                                                              self.c1 * r)
        return new_v

    def optimize(self, maxiter=200):
        for _ in range(maxiter):
            for i in range(self.n_particles):
                x = self.particles_pos[i]
                v = self.velocities[i]
                p_best = self.p_best[i]
                self.velocities[i] = self.update_velocity(x, v, p_best, self.g_best)
                self.particles_pos[i] = self.update_position(x, v)
                # Update the best position for particle i
                if self.calculating_f(self.particles_pos[i]) < self.calculating_f(p_best):
                    self.p_best[i] = self.particles_pos[i]
                # Update the best position overall
                if self.calculating_f(self.particles_pos[i]) < self.calculating_f(self.g_best):
                    self.g_best = self.particles_pos[i]
        return self.p_best, self.g_best

    def calculating_f(self, well):
        values_well = self.npv.calculated_NPV(well)
        return values_well
