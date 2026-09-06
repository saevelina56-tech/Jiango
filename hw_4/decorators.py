from django.http import HttpResponseForbidden
from functools import wraps

def group_required(*group_names):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.is_superuser:
                    return view_func(request, *args, **kwargs)
                if request.user.groups.filter(name__in=group_names).exists():
                    return view_func(request, *args, **kwargs)
            return HttpResponseForbidden('Доступ запрещен')
        return wrapper
    return decorator