from django.shortcuts import render, redirect
from globalData.decorator import login_required
from django.contrib import messages
from django.conf import settings
from django.http.response import JsonResponse
import requests
import json

# Create your views here.

@login_required
def map(request):
    ip = settings.IP
    headers = settings.HEADERS
    url = ip+f"/setup/category/?id={request.session['category']}"
    response = requests.request('GET',url,headers=headers)
    site_url = ip+f"/sites/?id={request.session['site']}"
    site_response = requests.request('GET',site_url,headers=headers)
    if request.method == "POST":
        category = request.POST.get('category')
        status = request.POST.get('status')
        params = {
            'category':category,
            'status':status
        }
        map_response = requests.request('GET',site_url,headers=headers,params=params)
        return render(request, 'pages/map-view.html',{'categories':response.json(), 'sites':map_response.json(),
        'selected_data': params})

    return render(request, 'pages/map-view.html',{'categories':response.json(), 'sites':site_response.json()})

@login_required
def getSites(request):
    ip = settings.IP
    category = request.GET['id']
    headers = settings.HEADERS
    params = {
        "category": category,
    }
    url = ip+f"/sites/?id={request.session['site']}"
    sites = requests.request("GET", url, headers=headers, params=params)
    return JsonResponse(sites.json(), safe=False)

@login_required
def getStation(request):
    ip = settings.IP
    headers = settings.HEADERS
    if request.GET.get('id'):
        site = request.GET.get('id')
        params = {
            "site_label": site,
        }
        url = ip+"/stations/"
        stations = requests.request("GET", url, headers=headers, params=params)
        return JsonResponse(stations.json(), safe=False)
    elif request.GET.get('label'):
        site_id = request.GET.get('label')
        params = {
            "site": site_id,
        }
        url = ip+"/stations/"
        stations = requests.request("GET", url, headers=headers, params=params)
        return JsonResponse(stations.json(), safe=False)
    else:
        return JsonResponse({}, safe=False)

@login_required
def getParameters(request):
    ip = settings.IP
    headers = settings.HEADERS
    if request.GET.get('id'):
        name = request.GET.get('id')
        params = {
            'station_name': name,
        }
        url = ip+"/parameters/"
        parameters = requests.request("GET", url, headers=headers, params=params)
        return JsonResponse(parameters.json(), safe=False)
    elif request.GET.get('station'):
        id = request.GET.get('station')
        params = {
            'station': id,
        }
        url = ip+"/parameters/"
        parameters = requests.request("GET", url, headers=headers, params=params)
        return JsonResponse(parameters.json(), safe=False) 

def get_parameters_values(request):
    ip = settings.IP
    headers = settings.HEADERS
    
    if request.GET.get('id'):
        parameter = request.GET.get('id')
        request.session['parameter']=parameter
        params = {
            'id': parameter,
        }
        url = ip+"/parameters/"
        parameters = requests.request("GET", url, headers=headers, params=params)
        return JsonResponse(parameters.json(), safe=False)


