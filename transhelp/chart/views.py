from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .computations.multivariate_gaussian import MultivariateGaussian


def gaussian(request):
    covariance_matrix_array = None

    def contains_covariance_parameters():
        for key in request.POST:
            if key.startswith("sigma-"):
                return True
        return False

    def get_val(pos_int):
        return float(request.POST["sigma-{}".format(pos_int)])

    if contains_covariance_parameters():
        covariance_matrix_array = [[get_val(11), get_val(12)], [get_val(21), get_val(22)]]

    try:
        multivariate_gaussian = MultivariateGaussian(covariance_matrix_array=covariance_matrix_array)
    except ValueError as e:
        return render(request, 'chart/gaussian.html', {"covariance_matrix" : covariance_matrix_array, "error_message" : str(e)})

    return render(request, 'chart/gaussian.html', multivariate_gaussian.get_batch_pdf())




