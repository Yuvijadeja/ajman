from django.shortcuts import render
import json 
import requests
import queue as Queue
import threading
from globalData.decorator import login_required
from django.conf import settings
import datetime
from django.contrib import messages
# Create your views here.


def getMatrixData(fromDate, toDate, site, station,interval, parameter, queue):
    ip = settings.IP
    headers = settings.HEADERS
    url = ip+f"/data/average?from={fromDate}&to={toDate}&site={site}&station={station}&parameters={parameter}&interval={interval}"
    get_response = (requests.request('GET', url, headers=headers))
    queue.put(get_response.json())

def getTimestamp(fromDate, toDate, interval, queue):
    timestamp = []
    fromDate = datetime.datetime.strptime(fromDate+" 00:00:00", "%Y-%m-%d %H:%M:%S")
    toDate = datetime.datetime.strptime(toDate+" 23:59:00", "%Y-%m-%d %H:%M:%S")
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
def multi_axis_report(request):
    queueData = Queue.Queue()
    queueTimestamp = Queue.Queue()
    ip = settings.IP
    headers = settings.HEADERS
    url = ip+f"/setup/category?id={request.session['category']}"
    response = requests.request('GET',url,headers=headers)

    if request.method == "POST":
        fromDate = request.POST['from']
        toDate = request.POST['to']
        category = request.POST['category']
        site = request.POST['site']
        station = request.POST['station']
        parameter1 = request.POST['parameter1']
        parameter2 = request.POST['parameter2']
        interval = request.POST['interval']
        parameters = [parameter1, parameter2]
        parameter_str = "&parameters="+parameter1+"&parameters="+parameter2
        
     
        thread1 = threading.Thread(target=getAverageData, args=[fromDate, toDate, site, station, interval, parameter_str, queueData], 
                                    name="thread1")
        thread1.start()
        thread2 = threading.Thread(target=getTimestamp, args=[fromDate, toDate, interval, queueTimestamp], name="thread2")
        thread2.start()

        thread1.join()
        thread2.join()

        data_response = queueData.get()
        timestamp = queueTimestamp.get()
        
        parameter_data = []
        for key, value in data_response.items():
            if len(value) > 0:
                parameter_data.append([value.get(k, "NA") for k in timestamp])

        
        timeseries = json.dumps(timestamp, indent=4, sort_keys=True, default=str),
    
        selected_data = {
            'from': fromDate,
            'to': toDate,
            'category': category,
            'site': site,
            'station': station,
            'parameter1': parameter1,
            'parameter2': parameter2,
            'interval':interval
        }
        return render(request,'pages/multi-axis.html', {'categories':response.json(), 'timestamp': timeseries, 'charts_data': parameter_data,
        'parameters': parameters,'selected_data': selected_data})
   
    return render(request,'pages/multi-axis.html',{'categories':response.json()})
            
@login_required
def matrix_report(request):
    queueData = Queue.Queue()
    queueTimestamp = Queue.Queue()
    queueStatData = Queue.Queue()
   
    ip = settings.IP
    headers = settings.HEADERS
    url = ip+f"/setup/category?id={request.session['category']}"
    response = requests.request('GET',url,headers=headers)

    if request.method == "POST":
        fromDate = request.POST['from']
        toDate = request.POST['from']
        category = request.POST['category']
        site = request.POST['site']
        station = request.POST['station']
        parameters = request.POST['parameter']
        interval = 60

        
        parameter_str = "&parameters="+parameters
        thread0 = threading.Thread(target=getStatData, args=[fromDate, toDate, site, station, parameter_str, queueStatData], 
                                    name="thread0")
        thread0.start()
        
        thread1 = threading.Thread(target=getMatrixData, args=[fromDate, toDate, site, station,interval, parameters, queueData], 
                                    name="thread1")
        
        thread2 = threading.Thread(target=getTimestamp, args=[fromDate, toDate, interval, queueTimestamp], name="thread2")
        thread2.start()
        thread2.join()
        
        
        thread1.start()
        thread1.join()
        data_response = queueData.get()
        timestamp = queueTimestamp.get()
        
        
        parameter_data = []
        for key, value in data_response.items():
            if len(value) > 0:
                parameter_data.append([value.get(k, "NA") for k in timestamp])
           
        data=[]
        stat_data={}
        if len(parameter_data) > 0:
            for i in range(len(parameter_data)):
                    sub_list = []
                    sub_list.append(timestamp[i])
                    for d in parameter_data[i]:
                        sub_list.append(d)
                    data.append(sub_list)
            
            thread0.join()
            stat_data = queueStatData.get()
        else:
            messages.warning(request, "Oops! no any data found.")
         
        date=[]   
        for value in data:
            value_date = value[0][:10]
            date.append(value_date)

        selected_data = {
            'from': fromDate,
            'to': toDate,
            'category': category,
            'site': site,
            'station': station,
            'interval': interval,
            'parameter':parameters
           
        }
        return render(request,'pages/matrix-report.html',{'categories':response.json(),'data': data,
        'stat_data': stat_data, 'parameters': parameters, 'selected_data': selected_data,'date':date})
        
    return render(request,'pages/matrix-report.html',{'categories':response.json()})


