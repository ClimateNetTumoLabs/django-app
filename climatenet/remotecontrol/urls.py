from django.contrib.auth.decorators import login_required
from .decorators import custom_login_required
from django.urls import path
from . import views


urlpatterns = [
    path('', login_required(views.home), name='remote-control'),
    path('submit_command_request/', custom_login_required(views.submit_command_request), name='submit_command_request'),
    path('submit_result_as_file_request/', custom_login_required(views.submit_result_as_file_request), name='submit_result_as_file_request'),
    path('submit_file_request/', custom_login_required(views.submit_file_request), name='submit_file_request'),
    path('submit_file_transfer/', custom_login_required(views.submit_file_transfer), name='submit_file_transfer'),
    path('logout/', views.logout_user, name='remote-control-logout'),
]
