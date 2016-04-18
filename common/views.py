from django.shortcuts import render

# Create your views here.

def home(request):
    """home
    to view top articles
    """
    # Pagination
    return render(request, "index.html")