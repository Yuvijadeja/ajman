from django.conf import settings
from django.shortcuts import render
import requests
from globalData.decorator import login_required
from django.core.exceptions import PermissionDenied

# Create your views here.
@login_required
def auditlogs(request):
    if request.session['role'] == "Admin":
        ip = settings.IP
        headers = settings.HEADERS
        user_url = ip+f"/users/list/?site={request.session['site']}"
        user_details = requests.request("GET", user_url, headers=headers)
        url = ip+"/audit-logs/"
        if request.method == "POST":
            user = request.POST.get('username')
            action = request.POST.get('action')
            params={
                'username':user,
                'action' :action 
            }
            auditlogs = requests.request("GET", url, headers=headers,params=params)
            return render(request, 'pages/audit-logs.html',{'auditlogs':auditlogs.json(),'user_details':user_details.json(),
            'selected_data': params})
        
        return render(request, 'pages/audit-logs.html',{'user_details':user_details.json()})
    else:
        raise PermissionDenied()