from django.shortcuts import render
from globalData.decorator import login_required
from django.contrib import messages
from django.conf import settings
import requests

# Create your views here.
@login_required
def email_logs(request):
    ip = settings.IP
    headers = settings.HEADERS
    
    user_url = ip+f"/users/list/?is_email=true"
    user_details = requests.request("GET", user_url, headers=headers)
    
    to = ""
    if request.method == "POST":
       to = request.POST.get('email')
        
    url=ip+f"/api/logs/email?page=1&to="+to
    if request.GET.get('link'):
        url=request.GET.get('link')+"&to="+to
    
    response=requests.request("GET", url, headers=headers)
    try:
        emails = response.json()['results']
        return render(request, 'pages/email-logs.html',{'emails':emails,
            'previous':response.json()['previous'], 'next':response.json()['next'],
            'user_details': user_details.json(), "to": to},)
    except:
        return render(request, 'pages/email-logs.html', {'user_details': user_details.json()})
    
def sms_logs(request):
    return render(request,"pages/sms-logs.html")