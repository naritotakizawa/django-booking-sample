import datetime
from django.shortcuts import resolve_url, get_object_or_404
from django.test import TestCase
from django.template.exceptions import TemplateDoesNotExist
from django.utils import timezone
from .models import Schedule, Staff

batu = '×'
maru = '○'
line = '-'


class StoreListViewTests(TestCase):
    fixtures = ['initial']

    def test_get(self):
        """店舗の一覧が表示されるかテスト"""
        response = self.client.get(resolve_url('booking:store_list'))
        self.assertQuerysetEqual(response.context['store_list'],  ['<Store: 店舗A>', '<Store: 店舗B>', '<Store: 店舗C>'])


class StaffListViewTests(TestCase):
    fixtures = ['initial']

    def test_store_a(self):
        """店舗Aのスタッフリストの確認"""
        response = self.client.get(resolve_url('booking:staff_list', pk=1))
        self.assertQuerysetEqual(response.context['staff_list'],  ['<Staff: 店舗A - じゃば>', '<Staff: 店舗A - ぱいそん>'])

    def test_store_b(self):
        """店舗Bのスタッフリストの確認"""
        response = self.client.get(resolve_url('booking:staff_list', pk=2))
        self.assertQuerysetEqual(response.context['staff_list'],  ['<Staff: 店舗B - じゃんご>'])

    def test_store_c(self):
        """店舗Cのスタッフリストの確認。店舗Cには誰もいない"""
        response = self.client.get(resolve_url('booking:staff_list', pk=3))
        self.assertQuerysetEqual(response.context['staff_list'],  [])


class StaffCalendarViewTests(TestCase):
    fixtures = ['initial']

    def test_no_schedule(self):
        """スケジュールがない場合のカレンダーをテスト。

        店名や表示期間と、「☓」がないことを確認。これがあるのはスケジュールがある場合。
        """
        start = timezone.localtime()
        end = start + datetime.timedelta(days=6)
        response = self.client.get(resolve_url('booking:calendar', pk=1))
        self.assertContains(response, '店舗A店 ぱいそん')
        self.assertContains(response, f'{start.year}年{start.month}月{start.day}日 - {end.year}年{end.month}月{end.day}日')
        self.assertContains(response, line)
        self.assertContains(response, maru)
        self.assertNotContains(response, batu)

    def test_one_schedule_next_day_9(self):
        """スケジュールが次の日の9時

        スケジュールがあるので、☓がカレンダー内に表示されることを確認
        """
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
        """スケジュールが次の日の8時

        8時のスケジュールはカレンダーに表示されないので、☓がないことを確認
        """
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
        """スケジュールが次の日の17時

        17時はカレンダーに表示されるので、☓があることを確認
        """
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
        """次の日の18時にスケジュール

        18時はカレンダー表示されないので、☓がないことを確認
        """
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
        """前の日の9時にスケジュール

        カレンダーは当日から表示なので、前の日のものは表示されない。☓がないことを確認。
        """
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
        """来週の9時にスケジュール

        7日後は表示されない。☓がないことを確認
        """
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
        """来週の9時にスケジュール

        7日後を基準にカレンダー表示するので、スケジュールは表示される。☓があることを確認。
        """
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
        """予約ページが表示されるかテスト"""
        now = timezone.localtime()
        response = self.client.get(resolve_url('booking:booking', pk=1, year=now.year, month=now.month, day=now.day, hour=9))
        self.assertContains(response, '店舗A店 ぱいそん')
        self.assertContains(response, f'{now.year}年{now.month}月{now.day}日 9時に予約')

    def test_post(self):
        """予約後に、カレンダーページで☓（予約あり）があることを確認"""
        now = timezone.localtime() + datetime.timedelta(days=1)
        response = self.client.post(
            resolve_url('booking:booking', pk=1, year=now.year, month=now.month, day=now.day, hour=9),
            {'name': 'テスト'},
            follow=True
        )
        messages = list(response.context['messages'])
        self.assertEqual(messages, [])
        self.assertContains(response, batu)

    def test_post_exists_data(self):
        """既に埋まった時間に予約した場合に、メッセージ表示があることを確認"""
        now = timezone.localtime().replace(hour=9, minute=0, second=0, microsecond=0)
        end = now + datetime.timedelta(hours=1)
        staff = get_object_or_404(Staff, pk=1)
        Schedule.objects.create(staff=staff, start=now, end=end, name='埋めた')
        response = self.client.post(
            resolve_url('booking:booking', pk=1, year=now.year, month=now.month, day=now.day, hour=9),
            {'name': 'これは入らない'},
            follow=True
        )
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), 'すみません、入れ違いで予約がありました。別の日時はどうですか。')


class MyPageViewTests(TestCase):
    fixtures = ['initial']

    def test_anonymous(self):
        """ログインしていない場合、ログインページにリダイレクトされることを確認"""
        response = self.client.get(resolve_url('booking:my_page'))
        self.assertRedirects(response, '/login/?next=%2Fmypage%2F')

    def test_login_admin(self):
        """管理者でログインした場合。店舗スタッフではないので、ナニも表示されない"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(resolve_url('booking:my_page'))
        self.assertQuerysetEqual(response.context['staff_list'], [])
        self.assertQuerysetEqual(response.context['schedule_list'], [])
        self.assertContains(response, 'adminのMyPage')

    def test_login_tanaka(self):
        """田中でログイン。スタッフデータが表示されることを確認"""
        self.client.login(username='tanakataro', password='helloworld123')
        response = self.client.get(resolve_url('booking:my_page'))
        self.assertQuerysetEqual(response.context['staff_list'], ['<Staff: 店舗B - じゃんご>', '<Staff: 店舗A - ぱいそん>'])
        self.assertQuerysetEqual(response.context['schedule_list'], [])
        self.assertContains(response, 'tanakataroのMyPage')

    def test_login_tanaka_with_schedule(self):
        """田中でログインし、予約がある場合、自分担当の予約だけ表示されるか確認。"""
        staff1 = get_object_or_404(Staff, pk=1)
        staff2 = get_object_or_404(Staff, pk=2)
        staff3 = get_object_or_404(Staff, pk=3)
        now = timezone.localtime()
        s1 = Schedule.objects.create(staff=staff1, start=now - datetime.timedelta(hours=1), end=now, name='テスト1')  # 過去の予約は表示されない
        s2 = Schedule.objects.create(staff=staff1, start=now + datetime.timedelta(hours=1), end=now, name='テスト2')  # 問題なく表示
        s3 = Schedule.objects.create(staff=staff2, start=now + datetime.timedelta(hours=1), end=now, name='テスト3')  # 問題なく表示
        s4 = Schedule.objects.create(staff=staff3, start=now + datetime.timedelta(hours=1), end=now, name='テスト4')  # staff3は、自分じゃない
        self.client.login(username='tanakataro', password='helloworld123')
        response = self.client.get(resolve_url('booking:my_page'))
        self.assertEqual(list(response.context['schedule_list']), [s2, s3])

    def test_login_yosida_with_schedule(self):
        """吉田でログインし、予約ある場合、自分担当の予約が表示されるか確認"""
        staff1 = get_object_or_404(Staff, pk=1)
        staff2 = get_object_or_404(Staff, pk=2)
        staff3 = get_object_or_404(Staff, pk=3)
        now = timezone.localtime()
        s1 = Schedule.objects.create(staff=staff1, start=now - datetime.timedelta(hours=1), end=now, name='テスト1')
        s2 = Schedule.objects.create(staff=staff1, start=now + datetime.timedelta(hours=1), end=now, name='テスト2')
        s3 = Schedule.objects.create(staff=staff2, start=now + datetime.timedelta(hours=1), end=now, name='テスト3')
        s4 = Schedule.objects.create(staff=staff3, start=now + datetime.timedelta(hours=1), end=now, name='テスト4')  # 吉田の予約
        self.client.login(username='yosidaziro', password='helloworld123')
        response = self.client.get(resolve_url('booking:my_page'))
        self.assertEqual(list(response.context['schedule_list']), [s4])
        self.assertContains(response, 'yosidaziroのMyPage')


class MyPageWithPkViewTests(TestCase):
    fixtures = ['initial']

    def test_anonymous(self):
        """ログインしていない場合、403の表示"""
        response = self.client.get(resolve_url('booking:my_page_with_pk', pk=2))
        self.assertEqual(response.status_code, 403)

    def test_login_admin(self):
        """スーパーユーザーは、どのユーザーのマイページでも見れる"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(resolve_url('booking:my_page_with_pk', pk=2))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tanakataroのMyPage')

    def test_login_tanaka(self):
        """自分自身のマイページは見れる"""
        self.client.login(username='tanakataro', password='helloworld123')
        response = self.client.get(resolve_url('booking:my_page_with_pk', pk=2))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tanakataroのMyPage')

    def test_login_yosida(self):
        """他人のマイページは見れない"""
        self.client.login(username='yosidaziro', password='helloworld123')
        response = self.client.get(resolve_url('booking:my_page_with_pk', pk=2))
        self.assertEqual(response.status_code, 403)

    def test_not_exist_user(self):
        """存在しないユーザーページにスーパーユーザーで行くと、404"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(resolve_url('booking:my_page_with_pk', pk=10000))
        self.assertEqual(response.status_code, 404)

    def test_not_exist_user(self):
        """存在しないユーザーページに一般ユーザーで行くと、403"""
        self.client.login(username='tanakataro', password='helloworld123')
        response = self.client.get(resolve_url('booking:my_page_with_pk', pk=10000))
        self.assertEqual(response.status_code, 403)


class MyPageCalendarViewTests(TestCase):
    fixtures = ['initial']

    def test_anonymous(self):
        """ログインしていない場合は403"""
        response = self.client.get(resolve_url('booking:my_page_calendar', pk=1))
        self.assertEqual(response.status_code, 403)

    def test_login_admin(self):
        """スーパーユーザーは、誰のカレンダーでも見れる"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(resolve_url('booking:my_page_calendar', pk=1))
        self.assertEqual(response.status_code, 200)

    def test_login_tanaka(self):
        """自分用のカレンダーは見れる"""
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
        """他人のカレンダーは見れない"""
        self.client.login(username='yosidaziro', password='helloworld123')
        response = self.client.get(resolve_url('booking:my_page_calendar', pk=1))
        self.assertEqual(response.status_code, 403)


class MyPageDayDetailViewTests(TestCase):
    fixtures = ['initial']

    def test_no_schedule(self):
        """店舗や日にちが正しく表示されるかの確認"""
        self.client.login(username='tanakataro', password='helloworld123')
        staff = get_object_or_404(Staff, pk=1)
        now = timezone.localtime().replace(hour=9, minute=0, second=0)
        response = self.client.get(resolve_url('booking:my_page_day_detail', pk=staff.pk, year=now.year, month=now.month, day=now.day))
        self.assertContains(response, '店舗A店 ぱいそん')
        self.assertContains(response, f'{now.year}年{now.month}月{now.day}日の予約一覧')

    def test_one_schedule_9(self):
        """予約が正しく表示されることを確認"""
        self.client.login(username='tanakataro', password='helloworld123')
        staff = get_object_or_404(Staff, pk=1)
        now = timezone.localtime().replace(hour=9, minute=0, second=0)
        Schedule.objects.create(staff=staff, start=now, end=now, name='テスト')
        response = self.client.get(resolve_url('booking:my_page_day_detail', pk=staff.pk, year=now.year, month=now.month, day=now.day))
        self.assertContains(response, 'テスト')

    def test_one_schedule_23(self):
        """時間外の予約は表示されないことを確認"""
        self.client.login(username='tanakataro', password='helloworld123')
        staff = get_object_or_404(Staff, pk=1)
        now = timezone.localtime().replace(hour=23, minute=0, second=0)
        Schedule.objects.create(staff=staff, start=now, end=now, name='テスト')
        response = self.client.get(resolve_url('booking:my_page_day_detail', pk=staff.pk, year=now.year, month=now.month, day=now.day))
        self.assertNotContains(response, 'テスト')


class MyPageScheduleViewTests(TestCase):
    fixtures = ['initial']

    def test_anonymous(self):
        """ログインしていないと403"""
        now = timezone.now()
        staff = get_object_or_404(Staff, pk=1)
        s1 = Schedule.objects.create(staff=staff, start=now, end=now, name='テスト')
        response = self.client.get(resolve_url('booking:my_page_schedule', pk=s1.pk))
        self.assertEqual(response.status_code, 403)

    def test_login_admin(self):
        """管理者は誰の予約でも詳細ページが見れる"""
        self.client.login(username='admin', password='admin123')
        now = timezone.now()
        staff = get_object_or_404(Staff, pk=1)
        s1 = Schedule.objects.create(staff=staff, start=now, end=now, name='テスト')
        response = self.client.get(resolve_url('booking:my_page_schedule', pk=s1.pk))
        self.assertContains(response, '店舗A店 ぱいそん')

    def test_login_tanaka(self):
        """自分担当の予約は、詳細ページが見れる"""
        self.client.login(username='tanakataro', password='helloworld123')
        now = timezone.now()
        staff = get_object_or_404(Staff, pk=1)
        s1 = Schedule.objects.create(staff=staff, start=now, end=now, name='テスト')
        response = self.client.get(resolve_url('booking:my_page_schedule', pk=s1.pk))
        self.assertContains(response, '店舗A店 ぱいそん')

    def test_login_yosida(self):
        """自分の担当じゃない予約は、詳細ページが見れない(403)"""
        self.client.login(username='yosidaziro', password='helloworld123')
        now = timezone.now()
        staff = get_object_or_404(Staff, pk=1)
        s1 = Schedule.objects.create(staff=staff, start=now, end=now, name='テスト')
        response = self.client.get(resolve_url('booking:my_page_schedule', pk=s1.pk))
        self.assertEqual(response.status_code, 403)

    def test_post(self):
        """予約の更新を行い、反映されるかのテスト"""
        self.client.login(username='tanakataro', password='helloworld123')
        now = timezone.now() + datetime.timedelta(days=1)
        staff = get_object_or_404(Staff, pk=1)
        s1 = Schedule.objects.create(staff=staff, start=now, end=now, name='テスト')
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')
        response = self.client.post(
            resolve_url('booking:my_page_schedule', pk=s1.pk),
            {'name': '更新しました', 'start': now_str, 'end': now_str},
            follow=True
        )
        self.assertEqual(list(response.context['schedule_list']), [s1])


class MyPageScheduleDeleteViewTests(TestCase):
    fixtures = ['initial']

    def test_get(self):
        """予約の削除ページ。GETアクセスは想定していないので、TemplateDoesNotExist"""
        self.client.login(username='tanakataro', password='helloworld123')
        now = timezone.now() + datetime.timedelta(days=1)
        staff = get_object_or_404(Staff, pk=1)
        s1 = Schedule.objects.create(staff=staff, start=now, end=now, name='テスト')
        with self.assertRaises(TemplateDoesNotExist):
            response = self.client.get(resolve_url('booking:my_page_schedule_delete', pk=s1.pk),)

    def test_post(self):
        """予約を削除すると当然、マイページの一覧には表示されなくなる"""
        self.client.login(username='tanakataro', password='helloworld123')
        now = timezone.now() + datetime.timedelta(days=1)
        staff = get_object_or_404(Staff, pk=1)
        s1 = Schedule.objects.create(staff=staff, start=now, end=now, name='テスト')
        response = self.client.post(
            resolve_url('booking:my_page_schedule_delete', pk=s1.pk),
            follow=True
        )
        self.assertEqual(list(response.context['schedule_list']), [])


class MyPageHolidayAddViewTests(TestCase):
    fixtures = ['initial']

    def test_anonymous(self):
        """ログインしていないと403"""
        now = timezone.now()
        staff = get_object_or_404(Staff, pk=1)
        response = self.client.post(
            resolve_url('booking:my_page_holiday_add', pk=staff.pk, year=now.year, month=now.month, day=now.day, hour=9),
            follow=True,
        )
        self.assertEqual(response.status_code, 403)

    def test_login_admin(self):
        """スーパーユーザーは、休日追加を自由に行える"""
        self.client.login(username='admin', password='admin123')
        now = timezone.now()
        staff = get_object_or_404(Staff, pk=1)
        response = self.client.post(
            resolve_url('booking:my_page_holiday_add', pk=staff.pk, year=now.year, month=now.month, day=now.day, hour=9),
            follow=True,
        )
        self.assertContains(response, '休暇(システムによる追加)')
        self.assertEqual(response.status_code, 200)

    def test_login_tanaka(self):
        """自分で休日を追加できることを確認"""
        self.client.login(username='tanakataro', password='helloworld123')
        now = timezone.now()
        staff = get_object_or_404(Staff, pk=1)
        response = self.client.post(
            resolve_url('booking:my_page_holiday_add', pk=staff.pk, year=now.year, month=now.month, day=now.day, hour=9),
            follow=True,
        )
        self.assertContains(response, '休暇(システムによる追加)')
        self.assertEqual(response.status_code, 200)

    def test_login_yosida(self):
        """他人の休日は追加できないことを確認"""
        self.client.login(username='yosidaziro', password='helloworld123')
        now = timezone.now()
        staff = get_object_or_404(Staff, pk=1)
        response = self.client.post(
            resolve_url('booking:my_page_holiday_add', pk=staff.pk, year=now.year, month=now.month, day=now.day, hour=9),
            follow=True,
        )
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        """GETでアクセスできないことを確認"""
        self.client.login(username='admin', password='admin123')
        now = timezone.now()
        staff = get_object_or_404(Staff, pk=1)
        response = self.client.get(
            resolve_url('booking:my_page_holiday_add', pk=staff.pk, year=now.year, month=now.month, day=now.day, hour=9),
            follow=True,
        )
        self.assertEqual(response.status_code, 405)

