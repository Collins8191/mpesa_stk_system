
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from payments.views import test_mpesa, mpesa_callback,payment_status, payment_history, payment_detail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test-mpesa/', test_mpesa),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('mpesa/callback/', mpesa_callback),
    path('payment-status/<str:checkout_request_id>/', payment_status),
    path('payment-history/', payment_history),
    path('payment/<int:payment_id>/', payment_detail),
]