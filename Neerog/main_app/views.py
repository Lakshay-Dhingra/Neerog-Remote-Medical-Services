
from django.shortcuts import render

# render syntax:
# return render(request,'page.html',context_var_dictionary)

# Create your views here.
def index(request):
    return render(request,'main_app/index.html')
