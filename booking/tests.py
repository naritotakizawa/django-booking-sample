import datetime
from django.shortcuts import resolve_url, get_object_or_404
from django.test import TestCase
from django.utils import timezone
from .models import Schedule, Staff

batu = '×'
maru = '○'
line = '-'


class StoreListViewTests(TestCase):
    fixtures = ['initial']

    def test_get(self):
        response = self.client.get(resolve_url('booking:store_list'))
        self.assertQuerysetEqual(response.context['store_list'],  ['<Store: 店舗A>', '<Store: 店舗B>', '<Store: 店舗C>'])


class StaffListViewTests(TestCase):
    fixtures = ['initial']

    def test_store_a(self):
        response = self.client.get(resolve_url('booking:staff_list', pk=1))
        self.assertQuerysetEqual(response.context['staff_list'],  ['<Staff: 店舗A - じゃば>', '<Staff: 店舗A - ぱいそん>'])

    def test_store_b(self):
        response = self.client.get(resolve_url('booking:staff_list', pk=2))
        self.assertQuerysetEqual(response.context['staff_list'],  ['<Staff: 店舗B - じゃんご>'])

    def test_store_c(self):
        response = self.client.get(resolve_url('booking:staff_list', pk=3))
        self.assertQuerysetEqual(response.context['staff_list'],  [])


class StaffCalendarViewTests(TestCase):
    fixtures = ['initial']

    def test_no_schedule(self):
        start = timezone.localtime()
        end = start + datetime.timedelta(days=6)
        response = self.client.get(resolve_url('booking:calendar', pk=1))
        self.assertContains(response, '店舗A店 ぱいそん')
        self.assertContains(response, f'{start.year}年{start.month}月{start.day}日 - {end.year}年{end.month}月{end.day}日')
        self.assertContains(response, line)
        self.assertContains(response, maru)
        self.assertNotContains(response, batu)

    def test_one_schedule_next_day_9(self):
        staff = get_object_or_404(Staff, pk=1)
        start = timezone.localtime() + datetime.timedelta(days=1)
        start = start.replace(hour=9, minute=0, second=0)
        end = start + datetime.timedelta(hours=1)
        Schedule.objects.create(staff=staff, start=start, end=end, name='テスト')
        response = self.client.get(resolve_url('booking:calendar', pk=staff.pk))
        self.assertContains(response, line)
        self.assertContains(response, maru)
        self.assertContains(response, batu)

    def test_one_schedule_next_day_8(self):
        staff = get_object_or_404(Staff, pk=1)
        start = timezone.localtime() + datetime.timedelta(days=1)
        start = start.replace(hour=8, minute=0, second=0)
        end = start + datetime.timedelta(hours=1)
        Schedule.objects.create(staff=staff, start=start, end=end, name='テスト')
        response = self.client.get(resolve_url('booking:calendar', pk=staff.pk))
        self.assertContains(response, line)
        self.assertContains(response, maru)
        self.assertNotContains(response, batu)

    def test_one_schedule_next_day_17(self):
        staff = get_object_or_404(Staff, pk=1)
        start = timezone.localtime() + datetime.timedelta(days=1)
        start = start.replace(hour=17, minute=0, second=0)
        end = start + datetime.timedelta(hours=1)
        Schedule.objects.create(staff=staff, start=start, end=end, name='テスト')
        response = self.client.get(resolve_url('booking:calendar', pk=staff.pk))
        self.assertContains(response, line)
        self.assertContains(response, maru)
        self.assertContains(response, batu)

    def test_one_schedule_next_day_18(self):
        staff = get_object_or_404(Staff, pk=1)
        start = timezone.localtime() + datetime.timedelta(days=1)
        start = start.replace(hour=18, minute=0, second=0)
        end = start + datetime.timedelta(hours=1)
        Schedule.objects.create(staff=staff, start=start, end=end, name='テスト')
        response = self.client.get(resolve_url('booking:calendar', pk=staff.pk))
        self.assertContains(response, line)
        self.assertContains(response, maru)
        self.assertNotContains(response, batu)

    def test_one_schedule_before_day_9(self):
        staff = get_object_or_404(Staff, pk=1)
        start = timezone.localtime() - datetime.timedelta(days=1)
        start = start.replace(hour=9, minute=0, second=0)
        end = start + datetime.timedelta(hours=1)
        Schedule.objects.create(staff=staff, start=start, end=end, name='テスト')
        response = self.client.get(resolve_url('booking:calendar', pk=staff.pk))
        self.assertContains(response, line)
        self.assertContains(response, maru)
        self.assertNotContains(response, batu)

    def test_one_schedule_next_week_9(self):
        staff = get_object_or_404(Staff, pk=1)
        start = timezone.localtime() + datetime.timedelta(days=7)
        start = start.replace(hour=9, minute=0, second=0)
        end = start + datetime.timedelta(hours=1)
        Schedule.objects.create(staff=staff, start=start, end=end, name='テスト')
        response = self.client.get(resolve_url('booking:calendar', pk=staff.pk))
        self.assertContains(response, line)
        self.assertContains(response, maru)
        self.assertNotContains(response, batu)

    def test_one_schedule_next_week_9_and_move(self):
        staff = get_object_or_404(Staff, pk=1)
        start = timezone.localtime() + datetime.timedelta(days=7)
        start = start.replace(hour=9, minute=0, second=0)
        end = start + datetime.timedelta(hours=1)
        Schedule.objects.create(staff=staff, start=start, end=end, name='テスト')
        response = self.client.get(resolve_url('booking:calendar', pk=staff.pk, year=start.year, month=start.month, day=start.day))
        self.assertContains(response, line)
        self.assertContains(response, maru)
        self.assertContains(response, batu)

        end = start + datetime.timedelta(days=6)
        self.assertContains(response, '店舗A店 ぱいそん')
        self.assertContains(response, f'{start.year}年{start.month}月{start.day}日 - {end.year}年{end.month}月{end.day}日')


class BookingViewTests(TestCase):
    fixtures = ['initial']

    def test_get(self):
        now = timezone.localtime()
        response = self.client.get(resolve_url('booking:booking', pk=1, year=now.year, month=now.month, day=now.day, hour=9))
        self.assertContains(response, '店舗A店 ぱいそん')
        self.assertContains(response, f'{now.year}年{now.month}月{now.day}日 9時に予約')

    def test_post(self):
        now = timezone.localtime()
        response = self.client.post(
            resolve_url('booking:booking', pk=1, year=now.year, month=now.month, day=now.day, hour=9),
            {'name': 'テスト'},
            follow=True
        )
        messages = list(response.context['messages'])
        self.assertEqual(messages, [])

    def test_post_exists_data(self):
        now = timezone.localtime().replace(hour=9)
        staff = get_object_or_404(Staff, pk=1)
        Schedule.objects.create(staff=staff, start=now, end=now, name='テスト')
        response = self.client.post(
            resolve_url('booking:booking', pk=1, year=now.year, month=now.month, day=now.day, hour=9),
            {'name': 'テスト'},
            follow=True
        )
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), 'すみません、入れ違いで予約がありました。別の日時はどうですか。')


class MyPageViewTests(TestCase):
    fixtures = ['initial']

    def test_anonymous(self):
        response = self.client.get(resolve_url('booking:my_page'))
        self.assertRedirects(response, '/login/?next=%2Fmypage%2F')

    def test_login_admin(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(resolve_url('booking:my_page'))
        self.assertQuerysetEqual(response.context['staff_list'], [])
        self.assertQuerysetEqual(response.context['schedule_list'], [])

    def test_login_tanaka(self):
        self.client.login(username='tanakataro', password='helloworld123')
        response = self.client.get(resolve_url('booking:my_page'))
        self.assertQuerysetEqual(response.context['staff_list'], ['<Staff: 店舗B - じゃんご>', '<Staff: 店舗A - ぱいそん>'])
        self.assertQuerysetEqual(response.context['schedule_list'], [])

    def test_login_tanaka_with_schedule(self):
        staff1 = get_object_or_404(Staff, pk=1)
        staff2 = get_object_or_404(Staff, pk=2)
        staff3 = get_object_or_404(Staff, pk=3)
        now = timezone.localtime()
        s1 = Schedule.objects.create(staff=staff1, start=now - datetime.timedelta(hours=1), end=now, name='テスト1')
        s2 = Schedule.objects.create(staff=staff1, start=now + datetime.timedelta(hours=1), end=now, name='テスト2')
        s3 = Schedule.objects.create(staff=staff2, start=now + datetime.timedelta(hours=1), end=now, name='テスト3')
        s4 = Schedule.objects.create(staff=staff3, start=now + datetime.timedelta(hours=1), end=now, name='テスト4')
        self.client.login(username='tanakataro', password='helloworld123')
        response = self.client.get(resolve_url('booking:my_page'))
        self.assertEqual(list(response.context['schedule_list']), [s2, s3])

    def test_login_yosida_with_schedule(self):
        staff1 = get_object_or_404(Staff, pk=1)
        staff2 = get_object_or_404(Staff, pk=2)
        staff3 = get_object_or_404(Staff, pk=3)
        now = timezone.localtime()
        s1 = Schedule.objects.create(staff=staff1, start=now - datetime.timedelta(hours=1), end=now, name='テスト1')
        s2 = Schedule.objects.create(staff=staff1, start=now + datetime.timedelta(hours=1), end=now, name='テスト2')
        s3 = Schedule.objects.create(staff=staff2, start=now + datetime.timedelta(hours=1), end=now, name='テスト3')
        s4 = Schedule.objects.create(staff=staff3, start=now + datetime.timedelta(hours=1), end=now, name='テスト4')
        self.client.login(username='yosidaziro', password='helloworld123')
        response = self.client.get(resolve_url('booking:my_page'))
        self.assertEqual(list(response.context['schedule_list']), [s4])


class MyPageWithPkViewTests(TestCase):
    fixtures = ['initial']

    def test_anonymous(self):
        response = self.client.get(resolve_url('booking:my_page_with_pk', pk=2))
        self.assertEqual(response.status_code, 403)

    def test_login_admin(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(resolve_url('booking:my_page_with_pk', pk=2))
        self.assertEqual(response.status_code, 200)

    def test_login_tanaka(self):
        self.client.login(username='tanakataro', password='helloworld123')
        response = self.client.get(resolve_url('booking:my_page_with_pk', pk=2))
        self.assertEqual(response.status_code, 200)

    def test_login_yosida(self):
        self.client.login(username='yosidaziro', password='helloworld123')
        response = self.client.get(resolve_url('booking:my_page_with_pk', pk=2))
        self.assertEqual(response.status_code, 403)


class MyPageCalendarViewTests(TestCase):
    fixtures = ['initial']

    def test_anonymous(self):
        response = self.client.get(resolve_url('booking:my_page_calendar', pk=1))
        self.assertEqual(response.status_code, 403)

    def test_login_admin(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(resolve_url('booking:my_page_calendar', pk=1))
        self.assertEqual(response.status_code, 200)

    def test_login_tanaka(self):
        self.client.login(username='tanakataro', password='helloworld123')
        response = self.client.get(resolve_url('booking:my_page_calendar', pk=1))
        self.assertEqual(response.status_code, 200)
        start = timezone.localtime()
        end = start + datetime.timedelta(days=6)
        self.assertContains(response, '店舗A店 ぱいそん')
        self.assertContains(response, f'{start.year}年{start.month}月{start.day}日 - {end.year}年{end.month}月{end.day}日')
        self.assertContains(response, line)
        self.assertContains(response, maru)
        self.assertNotContains(response, batu)

    def test_login_yosida(self):
        self.client.login(username='yosidaziro', password='helloworld123')
        response = self.client.get(resolve_url('booking:my_page_calendar', pk=1))
        self.assertEqual(response.status_code, 403)


class MyPageConfigViewTests(TestCase):
    fixtures = ['initial']

    def test_no_schedule(self):
        self.client.login(username='tanakataro', password='helloworld123')
        staff = get_object_or_404(Staff, pk=1)
        now = timezone.localtime().replace(hour=9, minute=0, second=0)
        response = self.client.get(resolve_url('booking:my_page_config', pk=staff.pk, year=now.year, month=now.month, day=now.day))
        self.assertContains(response, '店舗A店 ぱいそん')
        self.assertContains(response, f'{now.year}年{now.month}月{now.day}日の予約一覧')

    def test_one_schedule_9(self):
        self.client.login(username='tanakataro', password='helloworld123')
        staff = get_object_or_404(Staff, pk=1)
        now = timezone.localtime().replace(hour=9, minute=0, second=0)
        Schedule.objects.create(staff=staff, start=now, end=now, name='テスト')
        response = self.client.get(resolve_url('booking:my_page_config', pk=staff.pk, year=now.year, month=now.month, day=now.day))
        self.assertContains(response, 'テスト')

    def test_one_schedule_23(self):
        self.client.login(username='tanakataro', password='helloworld123')
        staff = get_object_or_404(Staff, pk=1)
        now = timezone.localtime().replace(hour=23, minute=0, second=0)
        Schedule.objects.create(staff=staff, start=now, end=now, name='テスト')
        response = self.client.get(resolve_url('booking:my_page_config', pk=staff.pk, year=now.year, month=now.month, day=now.day))
        self.assertNotContains(response, 'テスト')


class MyPageScheduleViewTests(TestCase):
    fixtures = ['initial']

    def test_anonymous(self):
        now = timezone.now()
        staff = get_object_or_404(Staff, pk=1)
        s1 = Schedule.objects.create(staff=staff, start=now, end=now, name='テスト')
        response = self.client.get(resolve_url('booking:my_page_schedule', pk=s1.pk))
        self.assertEqual(response.status_code, 403)

    def test_login_admin(self):
        self.client.login(username='admin', password='admin123')
        now = timezone.now()
        staff = get_object_or_404(Staff, pk=1)
        s1 = Schedule.objects.create(staff=staff, start=now, end=now, name='テスト')
        response = self.client.get(resolve_url('booking:my_page_schedule', pk=s1.pk))
        self.assertContains(response, '店舗A店 ぱいそん')

    def test_login_tanaka(self):
        self.client.login(username='tanakataro', password='helloworld123')
        now = timezone.now()
        staff = get_object_or_404(Staff, pk=1)
        s1 = Schedule.objects.create(staff=staff, start=now, end=now, name='テスト')
        response = self.client.get(resolve_url('booking:my_page_schedule', pk=s1.pk))
        self.assertContains(response, '店舗A店 ぱいそん')

    def test_login_yosida(self):
        self.client.login(username='yosidaziro', password='helloworld123')
        now = timezone.now()
        staff = get_object_or_404(Staff, pk=1)
        s1 = Schedule.objects.create(staff=staff, start=now, end=now, name='テスト')
        response = self.client.get(resolve_url('booking:my_page_schedule', pk=s1.pk))
        self.assertEqual(response.status_code, 403)

    def test_post(self):
        self.client.login(username='tanakataro', password='helloworld123')
        now = timezone.now() + datetime.timedelta(hours=9)
        staff = get_object_or_404(Staff, pk=1)
        s1 = Schedule.objects.create(staff=staff, start=now, end=now, name='テスト')
        response = self.client.post(
            resolve_url('booking:my_page_schedule', pk=s1.pk),
            {'name': '更新しました', 'start': '2020-01-01 09:00:00', 'end': '2020-01-01 09:00:00'},
            follow=True
        )
        self.assertEqual(list(response.context['schedule_list']), [s1])
