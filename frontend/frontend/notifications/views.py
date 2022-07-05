from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
import requests
from globalData.decorator import login_required

# Create your views here.
@login_required
def notifications(request):
    ip = settings.IP
    headers = settings.HEADERS
    id=request.session['id']
    if 'count' in request.session:
        if request.GET.get('action'):
            if request.GET.get('action') == 'next':
                request.session['count'] += 1
            elif request.GET.get('action') == 'prev':
                request.session['count'] -= 1
    else:
        request.session['count'] = 1
    page = request.session['count']
    notification_url=ip+f"/notifications/list?page={page}&recipient_id={id}"
    notification_response=requests.request("GET", notification_url, headers=headers)
    try:
        notifications = notification_response.json()['results']
        return render(request, 'pages/notifications.html',{'notifications':notifications,
            'previous':notification_response.json()['previous'], 'next':notification_response.json()['next']})

    except:
        messages.info(request, "Hurray no any pending notifications!")
        return render(request, 'pages/notifications.html')
    
@login_required
def delNotification(request):
    ip = settings.IP
    headers = settings.HEADERS
    notification_id = request.GET['id']
    notification_del_url = ip+"/notifications/destroy/"+notification_id+"/"
    notification_res = requests.request("DELETE",notification_del_url,headers=headers)
    if notification_res.json()['status'] == "success":
        messages.success(request, "Notification Deleted!")   
    else:
        messages.success(request, "Notification Not Deleted!")
    return redirect(notifications)