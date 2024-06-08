from django.urls import path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import dodaj_do_koszyka,docs_redirect

urlpatterns = [
    path('', views.main, name='home'),
    path('atrakcje/<int:atrakcja_id>/', views.atrakcja, name='atrakcja'),
    path('signup/', views.user_signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('koszyk/', views.koszyk, name='koszyk'),
    path('dodaj_do_koszyka/<int:atrakcja_id>/', dodaj_do_koszyka, name='dodaj_do_koszyka'),
    path('dodaj_do_koszyka_home/<int:atrakcja_id>/', views.dodaj_do_koszyka_home, name='dodaj_do_koszyka_home'),
    path('usun_z_koszyka/<int:item_id>/', views.usun_z_koszyka, name='usun_z_koszyka'),
    path('trasa/', views.trasa, name='trasa'),
    path('plany/', views.plany, name='plany'),
    path('plany/<int:plan_id>/', views.pojedynczy_plan, name='pojedynczy_plan'),
    path('pdf_download/', views.pdf_download, name='pdf_download'),
    path('plan_uzytkownika/', views.plan_uzytkownika, name='plan_uzytkownika'),
    path('zapisz_plan/', views.zapisz_plan, name='zapisz_plan'),
    path('usun_z_planu/<int:plan_id>/', views.usun_z_planu, name='usun_z_planu'),
    path('plan_do_koszyka/<int:plan_id>/', views.plan_do_koszyka, name='plan_do_koszyka'),
    path('send_mail/', views.send_mail, name='send_mail'),
    path('docs/', docs_redirect),
]
# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),

