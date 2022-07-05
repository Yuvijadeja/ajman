from django.shortcuts import render
from django.conf import settings
import requests
import threading
import queue as Queue
import json

def getparameter( parameter,queue):
    ip = settings.IP
    headers = settings.HEADERS
    url = ip+f"/parameters/?parameters={parameter}"
    data_response = (requests.request('GET', url, headers=headers))
    print(data_response)
    queue.put(data_response.json()) 

def setup(request):
    queueData = Queue.Queue()
    ip = settings.IP
    headers = settings.HEADERS
    url = ip+f"/setup/category?id={request.session['category']}"
    response = requests.request('GET',url,headers=headers)
    username=request.session['username']
    paramater=request.GET.get('parameter')
    
    if request.method == "POST":
        parameter_id=request.POST['parameter']
        normal_min = request.POST['normalmin']
        normal_max = request.POST['normalmax']
        normal_min = int(normal_min)
        if normal_min < 1:
            lower_max = normal_min
        else:
            lower_max = normal_min - 1

        update_url=ip+"/parameters/patch/"+str(parameter_id)
        payload=json.dumps({
            'normal_min':normal_min,
            'normal_max':normal_max,
            'lower_max': lower_max,
            'upper_min': int(normal_max) + 1
        })
        response = requests.request("PATCH", update_url, data=payload, headers=headers)
        return render(request, 'pages/setup.html',{'response':response.json()})
    
    return render(request,'pages/setup.html',{'categories':response.json()})