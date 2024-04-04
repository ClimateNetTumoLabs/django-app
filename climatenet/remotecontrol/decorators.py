"""
This module provides a decorator for custom login authentication in Django views.

Functions:
    - custom_login_required: Decorator function for custom login authentication.

Dependencies:
    - django.http.HttpResponse: Django HTTP response object.
"""

from django.http import HttpResponse


def custom_login_required(view_func):
    """
    Decorator function for custom login authentication.

    Parameters:
        - view_func (function): View function to be decorated.

    Returns:
        function: Decorated view function.
    """

    def wrapped_view(request, *args, **kwargs):
        """
        Wrapper function to check if the user is authenticated.

        Parameters:
            - request (django.http.HttpRequest): HTTP request object.
            - *args: Variable length argument list.
            - **kwargs: Arbitrary keyword arguments.

        Returns:
            django.http.HttpResponse: HTTP response object indicating login status.
        """
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponse(status=401)

    return wrapped_view
