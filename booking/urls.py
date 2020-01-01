from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.StoreList.as_view(), name='store_list'),
    path('login/', LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('store/<int:pk>/staffs/', views.StaffList.as_view(), name='staff_list'),
    path('staff/<int:pk>/calendar/', views.StaffCalendar.as_view(), name='calendar'),
    path('staff/<int:pk>/calendar/<int:year>/<int:month>/<int:day>/', views.StaffCalendar.as_view(), name='calendar'),
    path('staff/<int:pk>/booking/<int:year>/<int:month>/<int:day>/<int:hour>/', views.Booking.as_view(), name='booking'),

    path('mypage/', views.MyPage.as_view(), name='my_page'),
    path('mypage/<int:pk>/', views.MyPageWithPk.as_view(), name='my_page_with_pk'),
    path('mypage/<int:pk>/calendar/', views.MyPageCalendar.as_view(), name='my_page_calendar'),
    path('mypage/<int:pk>/calendar/<int:year>/<int:month>/<int:day>/', views.MyPageCalendar.as_view(), name='my_page_calendar'),
    path('mypage/<int:pk>/config/<int:year>/<int:month>/<int:day>/', views.MyPageDayDetail.as_view(), name='my_page_day_detail'),
    path('mypage/schedule/<int:pk>/', views.MyPageSchedule.as_view(), name='my_page_schedule'),
    path('mypage/schedule/<int:pk>/delete/', views.MyPageScheduleDelete.as_view(), name='my_page_schedule_delete'),
    path('mypage/holiday/add/<int:pk>/<int:year>/<int:month>/<int:day>/<int:hour>/', views.my_page_holiday_add, name='my_page_holiday_add'),
]

