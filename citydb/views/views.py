from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at the citydb index. The installation is working.")
