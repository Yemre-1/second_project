from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('' , views.home , name='home'),
    path('signup/' , views.signup_view , name='signup'),
    path('login/' , views.login_view , name='login'),
    path('logout/' , views.logout_view , name='logout'),
    path('profile/' , views.profile_view , name='profile'),
    path('profile/edit/' ,  views.edit_profile , name='edit_profile'),
    path('verify-email/<uuid:token>/' , views.verify_email , name='verify_email'),
    path('verify-email/<uuid:token>', views.verify_regist, name='verify_regist'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='main/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='main/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='main/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='main/password_reset_complete.html'), name='password_reset_complete'),
    path('product/list/', views.product_list, name='product_list'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('cart/remove/<int:item_id>/', views.remove_item, name='remove_item'),
    path('order/checkout/', views.checkout_view, name='checkout'),
    path('order/list', views.order_list , name='order_list'),
    path('order/detail/<int:order_id>', views.order_detail, name='order_detail'),
    path('product/detail/<int:product_id>', views.product_detail, name='product_detail'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('search/', views.product_search, name='product_search'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)