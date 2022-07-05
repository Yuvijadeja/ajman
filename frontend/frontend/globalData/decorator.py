from django.shortcuts import render, redirect

def login_required(function):
    def _function(request,*args, **kwargs):
        if request.session.get('username') is None:
            return redirect('/login')
        return function(request, *args, **kwargs)
    return _function