from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

app_name = 'runscript'
urlpatterns = [
    path('', views.create_list, name="main"),
    path('list/<list_id>/', views.view_and_upload, name='view_and_upload'),
    path('<list_id>/manage_user/', views.manage_user, name='manage_user'),
    path('detail/<file_id>/', views.script_detail, name='detail'),
    path('<file_id>/change/', views.script_change, name='change'),
    path('<file_id>/change/confirmedit/', views.script_confirm_edit, name='confirm_edit'),
    path('<file_id>/change/confirmdelete/', views.script_confirm_delete, name='confirm_delete'),
    #path('list/<list_id>/logs/', views.logs, name='logs'),
    path('list/<int:pk>/logs/', views.Logs.as_view(), name='logs'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
