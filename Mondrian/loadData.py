import numpy

def syntheticData(file_name):
    f = open(file_name) #'../data/LazegaLawyers/ELfriend36.dat'
    data = numpy.loadtxt(f)
    return data.astype(numpy.int)

def load_data(file_name):
    f = open(file_name)  # '../data/LazegaLawyers/ELfriend36.dat'
    data = numpy.loadtxt(f)
    return data.astype(numpy.int)
