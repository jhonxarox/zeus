from django.shortcuts import render

from zeus.forms import uploadForm

import pandas as pd
from androguard import misc

# Create your views here.
def index(request):
    return render(request, 'index.html')

def result(request):
    if request.method == 'POST':
        form = uploadForm(request.POST, request.FILES)

        if form.is_valid():
            file_input = request.FILES['file_input']
            a, d, dx = misc.AnalyzeAPK(file_input.read())
            file_name = a.get_app_name()
            return render(request, 'result.html', {'file_name': 'file name : '+str(file_name)})
            # try:
            #     a, d, dx = misc.AnalyzeAPK(file_input)
            #     file_name = a.get_app_name()
            #     return render(request, 'result.html', {'file_name': 'file name : '+str(file_name)})
            # except:
            #     return render(request, 'result.html', {'file_name': 'file not loaded '+str(file_input)})

        else:
            file_name = 'False'
            return render(request, 'result.html', {'file_name': file_name})
    return render(request, 'result.html')