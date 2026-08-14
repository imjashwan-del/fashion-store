from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def staff_required(view_func):
    """
    Enforces, on the SERVER, that only an authenticated user with
    is_staff=True can reach a dashboard view.

    Security note: hiding the dashboard link from the navbar is not
    sufficient (see project brief). Every single dashboard URL is wrapped
    with this decorator, so direct URL access (e.g. typing /admin-dashboard/
    into the browser) is checked on every request, not just navigation
    through the UI. Unauthenticated visitors are redirected to the admin
    login page; authenticated-but-non-staff users get a 403.
    """

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url='dashboard:login')
        if not request.user.is_staff:
            raise PermissionDenied('You do not have permission to access the store dashboard.')
        return view_func(request, *args, **kwargs)

    return _wrapped
