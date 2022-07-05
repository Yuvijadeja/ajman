from django.shortcuts import render, redirect
from globalData.decorator import login_required
from django.contrib import messages
from django.conf import settings
import requests
import json
import datetime
# Create your views here.

def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        ip=settings.IP
        headers = settings.HEADERS
        login_url = ip+"/users/login/"
        payload = json.dumps({
            "username":username,
            "password":password
        })
        response = requests.request("POST", login_url, headers=headers, data=payload)
        print(response.json())
        status=response.json()['status']
        if status == "success":
            data = response.json()['data']
            if data['is_staff'] == True:
                request.session['id'] = data['id']
                request.session['username'] = data['username']
                request.session['name'] = data['displayName']
                request.session['role'] = data['role']
                request.session['mobile'] = data['mobile']
                request.session['email'] = data['email']
                request.session['site'] = ""
                request.session['label'] = ""
                request.session['site_name'] = ""
                request.session['category'] = ""
            else:
                request.session['id'] = data['id']
                request.session['username'] = data['username']
                request.session['name'] = data['displayName']
                request.session['role'] = data['role']
                request.session['mobile'] = data['mobile']
                request.session['email'] = data['email']
                request.session['site'] = data['site']
                request.session['label'] = data['label']
                request.session['site_name'] = data['site_name']
                request.session['category'] = data['category']

            request.session['is_staff'] = data['is_staff']
            request.session['is_superuser'] = data['is_superuser']

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
                "action": "User log in at "+timestamp,
                "ip_address": audit_ip
                })
            audit_response=requests.request('POST',audit_url,headers=headers,data=payload)
            return redirect(realtimedata)
        else: 
            messages.warning(request, "Please enter the correct username and password!")
    return render(request, 'pages/login.html')

@login_required
def realtimedata(request):
    ip = settings.IP
    headers = settings.HEADERS
    url = ip+"/parameters/realtime-values/"
    params = {
        'site':request.session['site']
    }
    realtime_response = requests.request('GET',url,headers=headers,params=params)
    realtime_site_url = ip+"/parameters/realtime-sites/"
    site_params = {'id':request.session['site']}
    realtime_site=requests.request("GET", realtime_site_url, headers=headers,params=site_params)

    return render(request, 'pages/realtime-data.html',{'realtime_data':realtime_response.json(), 'site_data': realtime_site.json()['data']})

@login_required
def dashboard(request):
    ip = settings.IP
    headers = settings.HEADERS
    username=request.session['username']
    url = ip+"/users/list/?username="+username
    widget_url = ip+"/widget/"
    data_url = ip+"/parameters/realtime-values"
    user_details = requests.request("GET", url, headers=headers)
    id=user_details.json()[0]["id"]
    user_params = {
        'user': id
    }
    widgets = requests.request("GET",widget_url,headers=headers, params=user_params)
    data = []
    for widget in widgets.json():
        params = {
            'site':widget['site'],
            'station':widget['station'],
            'parameter':widget['parameter']
        }
        print(params)
        get_data = requests.request("GET",data_url,headers=headers,params=params)
        print(get_data.json())
        for values in get_data.json():
            if widget['widget'] == "Gauge":
                if values[6] == "None":
                    values[6] = 0 
                gauge_data = [widget['widget'], widget['id'],values[4], values[6], values[7],values[11], values[12], values[13],
                values[14], values[17], values[18], values[19], values[20], values[8], values[9], values[15]]
                data.append(gauge_data)
            elif widget['widget'] == "Card":
                card_data = [widget['widget'], widget['id'],values[4], values[6], values[7],values[11], values[12], values[13],
                values[14], values[17], values[18], values[19], values[20], values[8], values[9], values[15]]
                data.append(card_data)
        
    return render(request, 'pages/dashboard.html',{'widgets':widgets.json(),'data':data, 'site_name': request.session['site_name']})

@login_required
def dashboardsetup(request):
    ip = settings.IP
    headers = settings.HEADERS
    url = ip+f"/sites?id={request.session['site']}"
    sites = requests.request("GET", url, headers=headers)
    widget_create_url = ip+"/widget/create/"
    username=request.session['username']
    url = ip+"/users/list/?username="+username
    user_details = requests.request("GET", url, headers=headers)
    id=user_details.json()[0]["id"]
    
    if request.method == "POST":
        site = request.POST['site']
        station = request.POST['station']
        parameter = request.POST['parameter']
        widget = request.POST['widget']
        payload=json.dumps({
            'user':id,
            'site':site,
            'station':station,
            'parameter':parameter,
            'widget':widget 
        })
        user_params = {
        'user': id
        }
        get_widgets= ip+"/widget/"
        widgets = requests.request("GET",get_widgets,headers=headers, params=user_params)
        parameter_id=[]
        for w in widgets.json():
            widget_parameter_id=w['parameter']
            parameter_id.append(widget_parameter_id)
            
        if parameter in parameter_id :
            messages.warning(request, "Widget Already Exist!")
        else:
            widget_response = requests.request("POST",widget_create_url,headers=headers,data=payload)
            if widget_response.status_code == 201:
                messages.success(request, "Widget created successfully!")
            return redirect(dashboard)
    return render(request, 'pages/dashboard-setup.html',{'sites':sites.json()})

@login_required
def delWidget(request):
    ip = settings.IP
    headers = settings.HEADERS
    widget_id = request.GET['id']
    widget_del_url = ip+"/widget/destroy/"+widget_id+"/"
    widget_res = requests.request("DELETE",widget_del_url,headers=headers)
    if widget_res.json()['status'] == "success":
        messages.success(request, "Widget Deleted!")   
    else:
        messages.success(request, "Widget Not Deleted!")

    return redirect(dashboard)

@login_required
def logout(request):
    username = request.session['username']
    ip = settings.IP
    headers = settings.HEADERS
    
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
        "action": "User log out at "+timestamp,
        "ip_address": audit_ip
        })
    audit_response=requests.request('POST',audit_url,headers=headers,data=payload)
    del request.session['username']
    return redirect(login)

def page_not_found(request, exception=None):
    return render(request, 'pages/404.html')

def page_forbidden(request, exception=None):
    return render(request, 'pages/403.html')

def internal_server_error(request, exception=None):
    return render(request, 'pages/500.html')

def bad_request(request, exception=None):
    return render(request, 'pages/400.html')