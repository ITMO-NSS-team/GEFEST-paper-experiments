import numpy as np


# reading and processing a data file
def read_data(path, deposit_size, field_size):
    '''
    path: the path to the field data file
    deposit_size: deposit size
    field_size: the size of a piece of the deposit
    '''

    file = open(path)
    data = np.array([line.strip().split() for line in file.readlines()], dtype=np.float)
    data_phi = data.reshape(deposit_size)

    # transition to the volume of oil in the cells in barell
    data = data_phi * (20 * 10 * 2) / (3.28 ** 3) / 0.159

    data_field = data[:field_size[0], :field_size[1], :field_size[2]]
    print(
        f'The data is correctly read and processed. Deposit size: {data.shape}. Size of the cut field: {data_field.shape}.')

    return data_field
