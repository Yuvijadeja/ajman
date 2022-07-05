from django.contrib import messages
from django.shortcuts import render
from globalData.decorator import login_required
from django.conf import settings

import queue as Queue
import threading
import datetime
import json
import requests

# Create your views here.

def getTimestamp(fromDate, toDate, interval, queue):
    timestamp = []
    fromDate = datetime.datetime.strptime(fromDate, "%Y-%m-%dT%H:%M")
    toDate = datetime.datetime.strptime(toDate, "%Y-%m-%dT%H:%M")
    date_time = fromDate
    time_delta = int(interval)
    while date_time < toDate:
        date_time += datetime.timedelta(minutes=time_delta)
        timestamp.append(datetime.datetime.strftime(date_time, "%Y-%m-%d %H:%M:%S"))
    queue.put(timestamp)

def getAverageData(fromDate, toDate, site, station, interval, parameter_str, queue):
    ip = settings.IP
    headers = settings.HEADERS
    data_url = ip+f"/data/average?from={fromDate}&to={toDate}&site={site}&station={station}&interval={interval}"+parameter_str
    data_response = (requests.request('GET', data_url, headers=headers))
    queue.put(data_response.json())

def getStatData(fromDate, toDate, site, station, parameter_str, queue):
    ip = settings.IP
    headers = settings.HEADERS
    stat_url = ip+f"/data/statistics?from={fromDate}&to={toDate}&site={site}&station={station}&interval=30"+parameter_str
    stat_response = (requests.request('GET', stat_url, headers=headers))
    queue.put(stat_response.json())

@login_required
def average(request):
    queueData = Queue.Queue()
    queueTimestamp = Queue.Queue()
    queueStatData = Queue.Queue()
    ip = settings.IP
    headers = settings.HEADERS
    
    url = ip+f"/setup/category?id={request.session['category']}"
    response = requests.request('GET',url,headers=headers)
    username=request.session['username']

    if request.method == "POST":
        fromDate = request.POST['from']
        toDate = request.POST['to']
        category = request.POST['category']
        site = request.POST['site']
        station = request.POST['station']
        parameters = request.POST.getlist('parameter')
        interval = request.POST['interval']
        view = request.POST.getlist('view')
        if view:
            view = True
        else:
            view = False

        parameter_str = ""
        for parameter in parameters:
            parameter_str += "&parameters="+parameter
        
        thread0 = threading.Thread(target=getStatData, args=[fromDate, toDate, site, station, parameter_str, queueStatData], 
                                    name="thread0")
        thread0.start()
        thread1 = threading.Thread(target=getAverageData, args=[fromDate, toDate, site, station, interval, parameter_str, queueData], 
                                    name="thread1")
        thread1.start()
        thread2 = threading.Thread(target=getTimestamp, args=[fromDate, toDate, interval, queueTimestamp], name="thread2")
        thread2.start()

        thread1.join()
        thread2.join()

        data_response = queueData.get()
        print(data_response)
        timestamp = queueTimestamp.get()

        parameter_data = []
        for key, value in data_response.items():
            if len(value) > 0:
                parameter_data.append([value.get(k, "NA") for k in timestamp])
            
        data = []
        charts_data = []
        stat_data = {}
        if view:
            if len(parameter_data) > 0 and len(parameter_data[0]) > 0:
                for i in range(0, len(parameter_data[0])):
                    sub_list = []
                    sub_list.append(timestamp[i])
                    for j in range(0, len(parameter_data)):
                        try:
                            sub_list.append(round(parameter_data[j][i], 2))
                        except:
                            sub_list.append("NA")
                    data.append(sub_list)
            else:
                messages.warning(request, "Oops! no any data found.")
        else:
            if len(parameter_data) > 0 and len(parameter_data[0]) > 0:
                count = 0
                for parameter in parameters:
                    parameter_url = ip+"/parameters"
                    chart_parameter_params = {
                        'station_name': station,
                        'parameter': parameter
                    }
                    chart_parameter_response = requests.request("GET", parameter_url, headers=headers, params=chart_parameter_params)
                    chart_ranges = {
                        'id': chart_parameter_response.json()[0]['id'],
                        'standard_limit': chart_parameter_response.json()[0]['standard_limit'],
                        'lower_min': chart_parameter_response.json()[0]['lower'],
                        'upper_max': chart_parameter_response.json()[0]['upper'],
                        'normal_min': chart_parameter_response.json()[0]['normal_min'],
                        'normal_max': chart_parameter_response.json()[0]['normal_max'],
                    }
                    charts_data.append([json.dumps(parameter), json.dumps(timestamp, indent=4, sort_keys=True, default=str),
                    parameter_data[count], chart_ranges])
                    count += 1
            else:
                messages.warning(request, "Oops! no any data found.")
        
        thread0.join()
        stat_data = queueStatData.get()
    
        selected_data = {
            'from': fromDate,
            'to': toDate,
            'category': category,
            'site': site,
            'station': station,
            'interval': interval,
            'view': view
        }
        
        meta_data = request.META.get('HTTP_X_FORWARDED_FOR')
        if meta_data:
            audit_ip = meta_data.split(',')[-1].strip()
        else:
            audit_ip = request.META.get('REMOTE_ADDR')
        
        audit_url= ip + "/audit-logs/create/"
        timestamp=str(datetime.datetime.now())
        
        payload=json.dumps({
            "timestamp": timestamp,
            "username": username,
            "action_type": "Create",
            "action": "User has generated Average Report at "+timestamp,
            "ip_address": audit_ip
            })
        audit_response=requests.request('POST',audit_url,headers=headers,data=payload)
        return render(request, 'pages/average-report.html',{'categories':response.json(), 'data': data, 'charts_data': charts_data,
        'stat_data': stat_data, 'parameters': parameters, 'selected_data': selected_data})
        
    return render(request, 'pages/average-report.html',{'categories':response.json(),})
