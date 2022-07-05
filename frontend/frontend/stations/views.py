from django.conf import settings
from django.shortcuts import render
from django.http.response import JsonResponse
import requests
from globalData.decorator import login_required

# Create your views here.
@login_required
def stations(request):
    ip = settings.IP
    headers = settings.HEADERS
    url = ip+f"/sites/?id={request.session['site']}"
    sites = requests.request("GET", url, headers=headers)
    station_url = ip+f"/stations/?site={request.session['site']}"
    station_response = requests.request("GET", station_url, headers=headers)
    if request.method == "POST":
        site = request.POST.get('site')
        monitoring = request.POST.get('monitoring')
        params = {
            'site':site,
            'monitoring_type':monitoring,
        }
        station_data = requests.request("GET", station_url, headers=headers,params=params)
        return render(request, 'pages/station-status.html',{'sites':sites.json(), 'station_response':station_data.json(), 
        'selected_data': params})
    return render(request, 'pages/station-status.html',{'sites':sites.json(), 'station_response':station_response.json()})

@login_required
def parameters(request):
    ip = settings.IP
    headers = settings.HEADERS
    url = ip+f"/sites/?id={request.session['site']}"
    sites = requests.request("GET", url, headers=headers)
    parameters_url = ip+f"/parameters/?site={request.session['site']}"
    parameters_response = requests.request("GET", parameters_url, headers=headers)
    if request.method == "POST":
        site = request.POST.get('site')
        station = request.POST.get('station')
        params = {
            'station_name':station
        }
        parameters_data = requests.request("GET", parameters_url, headers=headers,params=params)
        
        selected_data = {
            'site': site,
            'station': station
        }
        return render(request, 'pages/parameters.html',{'sites':sites.json(),'parameters_response':parameters_data.json(),
        'selected_data': selected_data})
        
    return render(request, 'pages/parameters.html',{'sites':sites.json(), 'parameters_response':parameters_response.json()})

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
