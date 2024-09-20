from django.urls import path
from . import views
app_name = "userauths"


urlpatterns = [
    path('user/sign-up/', views.register_view, name= "sign-up"),
    path('user/sign-in/', views.login_view, name="sign-in"),
    path('user/login/', views.sign_up_page, name="sign-up-page"),
    path('submit-contact/', views.submit_contact_form, name='submit_contact_form'),

]


user_accounts_paths = [
    path('account/', views.account_view, name="account"),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('logout', views.logout_view, name="logout"),
]

urlpatterns += user_accounts_paths