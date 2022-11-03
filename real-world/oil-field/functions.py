import copy

from gefest.core.structure.point import Point
from gefest.core.structure.structure import distance

from structures.simulation import simulation


class NPV():
    '''
    Objective function: NPV
    NPV = -C_capex + \sum_{t = 1}^T CF_t /(1 + r)^t,
    where C_capex - total drilling costs,
    CF_t - cash flow in period t,
    T - the number of time periods that are considered,
    r - discount rate
    '''

    def __init__(self, field, T: int = 50, geometry=None):
        '''
        Parameters: 
        
        data: np.array[float], porosity value on the grid
        road: list, road map 
        T: int, the number of time periods during which oil production will be performed
        '''
        self.field = field
        self.data = self.field.data
        self.T = T
        self.geometry = geometry

    def calculated_NPV(self, wells: 'list[well]', road=None, data=None, invalid_areas=[[], []]):
        '''
        Parameters:
        
        wells: 'list[well]', list of wells in the 'well' class format
        '''
        if data is None:
            data = copy.deepcopy(self.data)

        C_capex = sum([well.cost for well in wells])
        r = 0.01
        r_road = 3000
        simulation_ = simulation(wells, self.T, data)

        NPV_value = -C_capex
        for t in range(self.T):
            NPV_value += (simulation_[0][t] - simulation_[1][t]) / ((1 + r) ** t)

        if road is not None:
            for well in wells:
                NPV_value -= distance(Point(well.start[0], well.start[1]), road, self.geometry) * r_road

        return -NPV_value
