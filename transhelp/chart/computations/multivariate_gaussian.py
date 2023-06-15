# -*- coding: utf8 -*-
import numpy

class MultivariateGaussian:

    def __init__(self, covariance_matrix_array=None, mean_vector=None):
        if covariance_matrix_array == None:
            covariance_matrix_array = [[1, 0], [0, 1]]
        if mean_vector == None:
            mean_vector = [0, 0]
        self.mean_vector = numpy.array(mean_vector)
        assert self.mean_vector.shape == (2,)
        covariance_matrix_array = numpy.array(covariance_matrix_array)
        assert covariance_matrix_array.shape == (2, 2,)
        self.covariance_matrix = covariance_matrix_array
        try:
            self.inv_covariane_matrix = numpy.linalg.inv(self.covariance_matrix)
        except:
            raise ValueError("covariance matrix cannot be inverted")
        self.det = numpy.linalg.det(self.covariance_matrix)
        if self.det < 0:
            raise ValueError("covariance matrix can not have negative determinant")

    def get_pdf(self, x, y):
        x_vector = numpy.array([x, y])
        centr_vector = x_vector - self.mean_vector
        numerator = numpy.exp(-.5 * centr_vector.dot(self.covariance_matrix).dot(centr_vector))
        denominator = 2 * numpy.pi * numpy.sqrt(self.det)
        return numerator / denominator

    def get_batch_pdf(self, x_min=-10, x_max=10, x_step=.1, y_min=-10, y_max=10, y_step=.1):
        x_range = numpy.arange(x_min, x_max, x_step)
        y_range = numpy.arange(y_min, y_max, y_step)
        z_rows = []
        for x in x_range:
            row = []
            for y in y_range:
                row.append(self.get_pdf(x, y))
            z_rows.append(row)
        return {
            "x" : list(x_range),
            "y" : list(y_range),
            "z" : z_rows,
            "covariance_matrix" : self.covariance_matrix,
        }
