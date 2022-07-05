from django.http import Http404
from django.shortcuts import render, redirect
from requests_http_signature import HTTPSignatureAuth
from base64 import b64decode
from django.conf import settings
from django.contrib import messages
from globalData.decorator import login_required

import requests

@login_required
def remotecalibration(request):
    ip = settings.IP
    headers = settings.HEADERS
    sites_url = ip+f"/sites/?id={request.session['site']}"
    sites = requests.request("GET", sites_url, headers=headers)
    url = ip+f"/parameters/calibration?site={request.session['site']}"
    parameters = requests.request("GET", url, headers=headers)
    if request.method == "POST":
        site=request.POST.get('site')
        station=request.POST.get('station')
        params={
            'station_name':station,
        }
        selected_data = {
            'site': site,
            'station': station
        }
        parameters = requests.request("GET", url, headers=headers, params=params)
        return render(request, 'pages/remote-calibration.html',{'parameters':parameters.json(),'sites':sites.json(),
        'selected_data': selected_data})
        
    return render(request, 'pages/remote-calibration.html',{'parameters':parameters.json(),'sites':sites.json()})

@login_required
def activateCalibration(request):
    ip = settings.IP
    headers = settings.HEADERS

    id = request.GET['id']
    type = request.GET['type']
    parameter_url = ip+"/parameters/calibration"
    parameter_params = {
        'id': id,
    }
    parameter = requests.request('GET', parameter_url, headers=headers, params=parameter_params)
    key_id =  'BOYSAV6M7AF5OH6ACMH5'
    key_secret_id = 'YuSAjd0Z8uWKUJogFZkJTFTCI9wKd3H/fyRBnBgt'
    api_key = 'MTYyQUVFRTEtOUI4Ny00OUNBLUJCMkItRjU5QkJDMjY0RTE4'
    
    host = 'api.remot3.it'
    url_path = '/apv/v27/device/connect'
    content_type_header = 'application/json'
    header = {
        'host': host,
        'content_type_header': content_type_header,
        'content_length_header': content_type_header,
        'DeveloperKey': api_key,
    }
    auth = HTTPSignatureAuth(algorithm="hmac-sha256", key=b64decode(key_secret_id), key_id=key_id)
    body = {
        "deviceaddress": parameter.json()[0]['address'],
        "wait": "true",
        "hostip": "0.0.0.0",
    }
    response = requests.post('https://' + host + url_path, auth=auth, headers=header, json=body)
    if response.status_code == 200:
        if response.json()['status'] == "true":
            ip = response.json()["connection"]["proxy"]
            if type == "Zero":
                relay_address = requests.get(ip + "/callibration?type=Zero")
                messages.success(request, type + " Callibration is activated.")
                
            elif type == "Span":
                relay_address = requests.get(ip + "/callibration?type=Span")
                messages.success(request, type + " Callibration is activated.")
            
            else:
                raise Http404     
        else:
            messages.error(request, "Device could not connect!")
    else:
        messages.error(request, "Data Logger not available!")
    
    return redirect(remotecalibration)

@login_required
def calibrationlogs(request):
    ip = settings.IP
    headers = settings.HEADERS
    calibration_logs_url = ip+f"/calibration/logs?site={request.session['site']}"
    calibration_logs = requests.request("GET",calibration_logs_url,headers=headers)
    print(calibration_logs.json())
    for values in calibration_logs.json():
        print(values)
        for key, value in values.items():
            print(key)
            print(value)
    return render(request, 'pages/calibration-logs.html',{'calibration_logs':calibration_logs.json()})