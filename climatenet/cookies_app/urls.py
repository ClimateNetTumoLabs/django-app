from django.urls import path
from .views import CollectUserDataView

urlpatterns = [
    path('collect/', CollectUserDataView.as_view(), name='collect_user_data'),

]