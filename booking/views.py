import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.views.decorators.http import require_POST
from .models import Store, Staff, Schedule

User = get_user_model()


class OnlyStaffMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        staff = get_object_or_404(Staff, pk=self.kwargs['pk'])
        return staff.user == self.request.user or self.request.user.is_superuser


class OnlyScheduleMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        schedule = get_object_or_404(Schedule, pk=self.kwargs['pk'])
        return schedule.staff.user == self.request.user or self.request.user.is_superuser


class OnlyUserMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.kwargs['pk'] == self.request.user.pk or self.request.user.is_superuser


class StoreList(generic.ListView):
    model = Store
    ordering = 'name'


class StaffList(generic.ListView):
    model = Staff
    ordering = 'name'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['store'] = self.store
        return context

    def get_queryset(self):
        store = self.store = get_object_or_404(Store, pk=self.kwargs['pk'])
        queryset = super().get_queryset().filter(store=store)
        return queryset


class StaffCalendar(generic.TemplateView):
    template_name = 'booking/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staff = get_object_or_404(Staff, pk=self.kwargs['pk'])
        today = datetime.date.today()

        # どの日を基準にカレンダーを表示するかの処理。
        # 年月日の指定があればそれを、なければ今日からの表示。
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        if year and month and day:
            base_date = datetime.date(year=year, month=month, day=day)
        else:
            base_date = today

        # カレンダーは1週間分表示するので、基準日から1週間の日付を作成しておく
        days = [base_date + datetime.timedelta(days=day) for day in range(7)]
        start_day = days[0]
        end_day = days[-1]

        # 9時から17時まで1時間刻み、1週間分の、値がTrueなカレンダーを作る
        calendar = {}
        for hour in range(9, 18):
            row = {}
            for day in days:
                row[day] = True
            calendar[hour] = row

        # カレンダー表示する最初と最後の日時の間にある予約を取得する
        start_time = datetime.datetime.combine(start_day, datetime.time(hour=9, minute=0, second=0))
        end_time = datetime.datetime.combine(end_day, datetime.time(hour=17, minute=0, second=0))
        for schedule in Schedule.objects.filter(staff=staff).exclude(Q(start__gt=end_time) | Q(end__lt=start_time)):
            local_dt = timezone.localtime(schedule.start)
            booking_date = local_dt.date()
            booking_hour = local_dt.hour
            if booking_hour in calendar and booking_date in calendar[booking_hour]:
                calendar[booking_hour][booking_date] = False

        context['staff'] = staff
        context['calendar'] = calendar
        context['days'] = days
        context['start_day'] = start_day
        context['end_day'] = end_day
        context['before'] = days[0] - datetime.timedelta(days=7)
        context['next'] = days[-1] + datetime.timedelta(days=1)
        context['today'] = today
        context['public_holidays'] = settings.PUBLIC_HOLIDAYS
        return context


class Booking(generic.CreateView):
    model = Schedule
    fields = ('name',)
    template_name = 'booking/booking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['staff'] = get_object_or_404(Staff, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        staff = get_object_or_404(Staff, pk=self.kwargs['pk'])
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        hour = self.kwargs.get('hour')
        start = datetime.datetime(year=year, month=month, day=day, hour=hour)
        end = datetime.datetime(year=year, month=month, day=day, hour=hour + 1)
        if Schedule.objects.filter(staff=staff, start=start).exists():
            messages.error(self.request, 'すみません、入れ違いで予約がありました。別の日時はどうですか。')
        else:
            schedule = form.save(commit=False)
            schedule.staff = staff
            schedule.start = start
            schedule.end = end
            schedule.save()
        return redirect('booking:calendar', pk=staff.pk, year=year, month=month, day=day)


class MyPage(LoginRequiredMixin, generic.TemplateView):
    template_name = 'booking/my_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['staff_list'] = Staff.objects.filter(user=self.request.user).order_by('name')
        context['schedule_list'] = Schedule.objects.filter(staff__user=self.request.user, start__gte=timezone.now()).order_by('name')
        return context


class MyPageWithPk(OnlyUserMixin, generic.TemplateView):
    template_name = 'booking/my_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_object_or_404(User, pk=self.kwargs['pk'])
        context['staff_list'] = Staff.objects.filter(user__pk=self.kwargs['pk']).order_by('name')
        context['schedule_list'] = Schedule.objects.filter(staff__user__pk=self.kwargs['pk'], start__gte=timezone.now()).order_by('name')
        return context


class MyPageCalendar(OnlyStaffMixin, StaffCalendar):
    template_name = 'booking/my_page_calendar.html'


class MyPageDayDetail(OnlyStaffMixin, generic.TemplateView):
    template_name = 'booking/my_page_day_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        staff = get_object_or_404(Staff, pk=pk)
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        date = datetime.date(year=year, month=month, day=day)

        # 9時から17時まで1時間刻みのカレンダーを作る
        calendar = {}
        for hour in range(9, 18):
            calendar[hour] = []

        # カレンダー表示する最初と最後の日時の間にある予約を取得する
        start_time = datetime.datetime.combine(date, datetime.time(hour=9, minute=0, second=0))
        end_time = datetime.datetime.combine(date, datetime.time(hour=17, minute=0, second=0))
        for schedule in Schedule.objects.filter(staff=staff).exclude(Q(start__gt=end_time) | Q(end__lt=start_time)):
            local_dt = timezone.localtime(schedule.start)
            booking_date = local_dt.date()
            booking_hour = local_dt.hour
            if booking_hour in calendar:
                calendar[booking_hour].append(schedule)

        context['calendar'] = calendar
        context['staff'] = staff
        return context


class MyPageSchedule(OnlyScheduleMixin, generic.UpdateView):
    model = Schedule
    fields = ('start', 'end', 'name')
    success_url = reverse_lazy('booking:my_page')


class MyPageScheduleDelete(OnlyScheduleMixin, generic.DeleteView):
    model = Schedule
    success_url = reverse_lazy('booking:my_page')


@require_POST
def my_page_holiday_add(request, pk, year, month, day, hour):
    staff = get_object_or_404(Staff, pk=pk)
    if staff.user == request.user or request.user.is_superuser:
        start = datetime.datetime(year=year, month=month, day=day, hour=hour)
        end = datetime.datetime(year=year, month=month, day=day, hour=hour + 1)
        Schedule.objects.create(staff=staff, start=start, end=end, name='休暇(システムによる追加)')
        return redirect('booking:my_page_day_detail', pk=pk, year=year, month=month, day=day)

    raise PermissionDenied
