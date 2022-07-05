import json
from django.shortcuts import render
import requests
from django.conf import settings
from django.contrib import messages
from globalData.decorator import login_required

# Create your views here.
@login_required
def myaccount(request):
    session_email=request.session['email']
    ip = settings.IP
    headers = settings.HEADERS
    username=request.session['username']
    url = ip+"/users/list/?username="+username
    user_details = requests.request("GET", url, headers=headers)
    id=user_details.json()[0]["id"]
    if request.method == "POST":
        name = request.POST['name']
        mobile = request.POST['mobile']
        email = request.POST['email']
        join = request.POST['joining']
        update_user_url=ip+"/users/patch/"+str(id)+"/"
        payload=json.dumps({
            'displayName': name,
            'mobile': mobile,
            'email': email,
            'join': join,
        })
        session_email=request.session['email']
        
        if email!=session_email:
            get_users= ip+"/users/list/"
            all_users = requests.request("GET",get_users,headers=headers)
            user_email=[]
            for u in all_users.json():
                u_email=u['email']
                user_email.append(u_email)
            if  email in user_email :
                messages.warning(request, "Email ID already exist")
            else:
                update_user_response=requests.request("PATCH", update_user_url, headers=headers,data=payload)
                request.session['email']=email
                user_details = requests.request("GET", url, headers=headers)
                messages.success(request, "User updated successfully!")
        else:
            update_user_response=requests.request("PATCH", update_user_url, headers=headers,data=payload)
            user_details = requests.request("GET", url, headers=headers)
            messages.success(request, "User updated successfully!")
    return render(request, 'pages/my-account.html',{'user_details':user_details.json()})
    
@login_required
def changepassword(request):
    ip = settings.IP
    headers = settings.HEADERS
    username=request.session['username']
    print(username)
    users_url = ip+"/users/list/?username="+username
    users_details = requests.request("GET", users_url, headers=headers)
    
    change_password_url = ip+"/users/change-password/"
    change_password_details = requests.request("GET", change_password_url, headers=headers)
    
    if request.method == "POST":
        user=username
        old_password = request.POST['oldpassword']
        new_password = request.POST['newpassword']
        payload=json.dumps({
            'username':user,
            'old_password':old_password,
            'new_password':new_password
        })
        update_user_password=requests.request("PATCH",change_password_url,headers=headers,data=payload)
        status=update_user_password.json()['status']
        
        if status=="success":
            messages.success(request, "Password changed!") 
        else:
            messages.warning(request, "Password can not changed! Please contact site administrator or try again.")
            
            
    return render(request, 'pages/change-password.html',{'user_details':users_details.json()})