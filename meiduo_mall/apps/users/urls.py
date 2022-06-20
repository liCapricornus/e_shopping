from django.urls import path
from apps.users.views import UsernameCountView,RegisterView,LoginView,LogoutView,CenterView,EmailView,EmailVerifyView,AddressCreateView
from apps.users.views import AddressView,AddressTitleView,AddressDefaultView,PasswordChangeView
urlpatterns = [
    # 判断用户名是否重复
    path('usernames/<username:username>/count',UsernameCountView.as_view()),
    path('register/',RegisterView.as_view()),
    path('login/',LoginView.as_view()),
    path('logout/',LogoutView.as_view()),
    path('info/',CenterView.as_view()),
    path('emails/',EmailView.as_view()),
    path('emails/verification/',EmailVerifyView.as_view()),
    path('addresses/create/',AddressCreateView.as_view()),
    path('addresses/',AddressView.as_view()),
    path('addresses/<addresses_id>/title/',AddressTitleView.as_view()),  # '/addresses/' + this.addresses[index].id + '/title/'
    path('addresses/<addresses_id>/default/',AddressDefaultView.as_view()),  #  '/addresses/' + this.addresses[index].id + '/default/'
    path('addresses/<addresses_id>/',AddressDefaultView.as_view()),
    path('password/',PasswordChangeView.as_view()),
]