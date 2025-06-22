# lab2/decorators.py
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def group_required(group_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.conf import settings
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)
            if not request.user.groups.filter(name=group_name).exists():
                raise PermissionDenied("У вас нет прав для доступа к этому разделу")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
