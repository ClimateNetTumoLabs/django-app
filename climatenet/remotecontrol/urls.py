from django.urls import path, re_path
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', login_required(views.home), name='remote-control'),
    path('login', views.login_user, name='remote-control-login'),
    path('submit_command_request/', login_required(views.submit_command_request), name='submit_command_request'),
    path('submit_command_file_request/', login_required(views.submit_command_file_request), name='submit_command_file_request'),
    path('submit_file_request/', login_required(views.submit_file_request), name='submit_file_request'),
    path('submit_file_transfer/', login_required(views.submit_file_transfer), name='submit_file_transfer'),
    path('logout/', login_required(views.logout_user), name='remote-control-logout'),
]
