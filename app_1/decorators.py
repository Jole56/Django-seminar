from django.shortcuts import redirect
from functools import wraps

def admin_required(function):
    @wraps(function)
    def wrap(request,*args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == 'admin':
                return function(request,*args, **kwargs)
            else:
                return redirect('home')
        else:
            return redirect('login')
    return wrap
