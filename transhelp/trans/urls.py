from django.urls import path, include

from . import views
from . import authviews

urlpatterns = [
    path('', views.list_recordings, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', authviews.register, name="register"),
    path('accounts/checkreglogin/', authviews.check_register_login, name="check-register-login"),
    path('trans/<int:rec_info_id>', views.trans, name="trans"),
    path('addrec/', views.add_recording, name="add-rec"),
    path('listrec/', views.list_recordings, name="list-rec"),
    path('gettrans/<int:rec_info_id>', views.get_trans_text, name="get-trans-text"),
    path('reginvitation', views.registration_invitation, name="reg-invitation"),
]
