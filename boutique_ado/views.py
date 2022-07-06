from django.shortcuts import render


def handler404(request, exception):
    """Error Handler 404 Pge no Found"""
    return render(request, "errors/404.html", status=404)