from django.shortcuts import render, redirect


def base_grid(request):

    return render(request, 'admin/base/grid_base.html')