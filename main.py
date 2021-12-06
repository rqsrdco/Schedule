__version__ = "0.3"
import os  # NOQA
import sys
import glob
import json
import threading
import logging  # NOQA
from typing import NoReturn  # NOQA
from datetime import datetime, timedelta, date, time  # NOQA


from kivy.utils import get_color_from_hex  # NOQA
from kivy.core.window import Window  # NOQA
from kivy.animation import Animation  # NOQA
from kivy import properties as P  # NOQA
from kivy.utils import platform  # NOQA
from kivy.lang import Builder  # NOQA
from kivy.clock import Clock, mainthread  # NOQA
from kivy.logger import Logger
from kivy.factory import Factory
from kivy.config import Config
from kivy.metrics import sp

from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivymd.uix.pickers import MDDatePicker, MDTimePicker

from oscpy.client import OSCClient
from oscpy.server import OSCThreadServer

if platform == 'android':
    from android import activity, mActivity
    from android.runnable import run_on_ui_thread
    from jnius import autoclass, cast, JavaException
    from android.config import ACTIVITY_CLASS_NAME, SERVICE_CLASS_NAME
    from android.storage import primary_external_storage_path
    from android.permissions import request_permissions, Permission

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Uri = autoclass('android.net.Uri')
    Intent = autoclass('android.content.Intent')
    Context = autoclass('android.content.Context')
    Settings = autoclass('android.provider.Settings')
    PowerManager = autoclass('android.os.PowerManager')
    PackageManager = autoclass('android.content.pm.PackageManager')

    from libs.applibs.toast import android_toast
    from libs.applibs.vibrator import AndroidVibrator
    from libs.applibs.alarm_schedule import RqsAlarmSchedule
    from libs.applibs.notification import cancel_notification, notify

    PACKAGE_NAME = u'org.rqsrd.schedule'
    SERVICE_NAME = u'{packagename}.Service{servicename}'.format(
        packagename=PACKAGE_NAME,
        servicename=u'Rqsrdservice',
    )
    APP_STARTUP_PERMISSIONS = [
        Permission.INTERNET,
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.FOREGROUND_SERVICE,
        Permission.WAKE_LOCK,
        Permission.VIBRATE,
        Permission.RECEIVE_BOOT_COMPLETED,
        Permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS
    ]
else:
    def run_on_ui_thread(*args, **kwargs):
        return

from libs.uix.baseclass.alarm_screen import AlarmScreen

if platform == 'android':
    SDK_INT = autoclass('android.os.Build$VERSION').SDK_INT
else:
    SDK_INT = None

_Debug = True
if _Debug:
    Config.set('kivy', 'log_level', 'debug')

Config.set('kivy', 'window_icon', 'assets/icons/logo.png')

if 'ANDROID_ARGUMENT' not in os.environ:
    Config.set('input', 'mouse', 'mouse,disable_multitouch')


class AlarmClockApp(MDApp):
    date_dialog = P.ObjectProperty()
    time_dialog = P.ObjectProperty()

    activity_alarm = P.BooleanProperty(False)

    alarm_default = {
        "alarm_time": "",
        "alarm_type": 0,
        "title": "",
        "ticker": "",
        "description": ""
    }

    reaction_value = [
        {
            "hours": 9,
            "minutes": 14
        },
        {
            "hours": 7,
            "minutes": 44
        },
        {
            "hours": 6,
            "minutes": 14
        },
        {
            "hours": 4,
            "minutes": 44
        }
    ]
    str_timestamp = "%a %d/%m/%Y %I:%M %p"
    timestamp_data = P.ObjectProperty(allownone=True)
    service = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = None
        self.icon = self.resource_path("assets/icons/logo.png")
        self.title = "Alarm Reaction"
        # themes = ["Red", "Pink", "Purple", "DeepPurple", "Indigo",..]
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.primary_hue = "A700"
        self.theme_cls.accent_palette = "Pink"
        self.theme_cls.accent_hue = "500"
        self.theme_cls.theme_style = "Light"
        # fonts
        from libs.applibs import i_fonts_definitions
        i_fonts_definitions.register_fonts()
        self.theme_cls.font_styles.update(
            i_fonts_definitions.font_styles
        )

    def resource_path(self, relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(
            os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def request_app_permissions(self, list_permissions=[]):
        global APP_STARTUP_PERMISSIONS
        print('AlarmClockApp.request_app_permissions')
        ret = request_permissions(list_permissions or APP_STARTUP_PERMISSIONS)
        print('AlarmClockApp.request_app_permissions : %r' % ret)

    def start_service(self):
        context = mActivity.getApplicationContext()
        SERVICE_NAME = str(context.getPackageName()) + \
            '.Service' + 'Rqsrdservice'
        self.service = autoclass(SERVICE_NAME)
        self.service.start(mActivity, '')

    def stop_service(self):
        self.client.send_message(b'/stop_service', [])
        self.service = None

    def build(self):
        Window.bind(on_keyboard=self.back_key_handler)
        self.server = server = OSCThreadServer()
        server.listen(
            address=b'localhost',
            port=3002,
            default=True,
        )
        server.bind(b'/date', self.date_msg)

        self.client = OSCClient(b'localhost', 3000)
        return AlarmScreen()

    def date_msg(self, msg):
        self.root.current_datetime = msg.decode('utf8')

    def back_key_handler(self, window, keycode1, keycode2, text, modifiers):
        if keycode1 in [27, 1001]:
            self.handle_exit_app()
        return True

    @mainthread
    def handle_exit_app(self):
        if platform == 'android':
            mActivity.moveTaskToBack(True)
            self.stop()

    def doze_opt_out(self):
        if platform != 'android':
            return
        context = mActivity.getApplicationContext()
        powerManager = cast(
            PowerManager, context.getSystemService(Context.POWER_SERVICE)
        )
        return powerManager.isIgnoringBatteryOptimizations(
            mActivity.getPackageName()
        )

    def allowe_opt_out_battery_optimazation(self, *_):
        is_opt_out = self.doze_opt_out()
        if not is_opt_out:
            mActivity.startActivity(
                Intent(
                    Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,
                    Uri.parse("package:"+mActivity.getPackageName())
                )
            )

    def init_date_picker(self):
        self.date_dialog = MDDatePicker(
            mode='picker',
            primary_color=get_color_from_hex("#72225b"),
            accent_color=get_color_from_hex("#5d1a4a"),
            selector_color=get_color_from_hex("#e93f39"),
            text_toolbar_color=get_color_from_hex("#cccccc"),
            text_color=("#ffffff"),
            text_current_color=get_color_from_hex("#e93f39"),
            input_field_background_color=(1, 1, 1, 0.2),
            input_field_text_color=(1, 1, 1, 1),
        )

    def init_time_picker(self):
        today = datetime.today()
        self.time_dialog = MDTimePicker()
        self.time_dialog.set_time(time(hour=today.hour, minute=today.minute))

    def on_start(self):
        print("App.on_start")
        if platform == 'android':
            # self.request_app_permissions()
            self.start_service()
            activity.bind(on_new_intent=self.on_new_intent)
            self.on_new_intent(mActivity.getIntent())
        self.load_alarm_scheduled()
        Clock.schedule_interval(self.root.update_current_datetime_guest, 1)

    def on_pause(self):
        print("App.on_pause")
        Clock.unschedule(self.root.update_current_datetime_guest)
        self.stop_service()
        return True

    def on_resume(self):
        print("App.on_resume")
        print(os.environ['ANDROID_ARGUMENT'])
        Clock.schedule_interval(self.root.update_current_datetime_guest, 1)
        self.start_service()

    def on_stop(self):
        print("App.on_stop")

    @mainthread
    def on_new_intent(self, intent):
        print("---------App.on_new_intent---------")
        print("intent.getAction() = ", intent.getAction())
        print("intent.getPackage() = ", intent.getPackage())
        print("intent.getExtras() = ", intent.getExtras())
        print("intent.getFlags() = ", intent.getFlags())
        print(intent.getBooleanExtra("alarmIsOn", False),
              intent.getStringExtra("exit"))
        if intent.getStringExtra("exit") == "exit":
            self.handle_exit_app()
        if intent.getBooleanExtra("alarmIsOn", False):
            self.root.alarm_option.option_timestamp = None
            self.timestamp_data = None
            self.save_scheduled_task(self.alarm_default)
            self.activity_alarm = False
            cancel_notification()
            RqsAlarmSchedule().dimiss_alarm()
        print("---------App.on_new_intent---------")

    def on_timestamp_data(self, instance, value):
        if value is None:
            self.root.alarm_option.ids.lbl_time.font_size = sp(14)
            Clock.unschedule(self.show_time_remain)
        else:
            self.root.alarm_option.ids.lbl_time.font_size = sp(18)
            Clock.schedule_interval(self.show_time_remain, 1)

    def show_time_remain(self, dt):
        now = datetime.now()
        timeDelta = self.timestamp_data - now
        hours, remainder = divmod(timeDelta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        _text = "Còn "
        if hours > 0:
            _text += "%s giờ " % str(hours).zfill(2)
        if minutes > 0:
            _text += "%s phút " % str(minutes).zfill(2)
            if seconds % 2 == 0:
                _text += "(^_^)"
            if seconds % 2 != 0:
                _text += "(-_-)"
        if minutes == 0 and hours == 0:
            if seconds % 2 == 0:
                _text = "~(^_^)~"
            if seconds % 2 != 0:
                _text = "_(-_-)_"
        self.root.alarm_option.text = _text

    def load_alarm_scheduled(self):
        task = self.load_scheduled_task()
        if (not(task.get("alarm_time") and task.get("alarm_time").strip())):
            self.root.alarm_option.option_timestamp = None
            self.timestamp_data = None
        else:
            alarm_datetime = datetime.strptime(
                task.get("alarm_time"),
                self.str_timestamp
            )
            self.timestamp_data = alarm_datetime
            now = datetime.now()
            if alarm_datetime > now:
                self.root.alarm_option.option_timestamp = alarm_datetime
                self.activity_alarm = True
            else:
                self.root.alarm_option.option_timestamp = None
                self.timestamp_data = None
                self.save_scheduled_task(self.alarm_default)
                self.activity_alarm = False
                cancel_notification()
                RqsAlarmSchedule().dimiss_alarm()

    def set_alarm(self, object):
        if not self.activity_alarm:
            if object.option_timestamp is None:
                android_toast("Chưa chọn mốc thời gian báo thức ?")
            else:
                if object.id_type == 2:
                    title = "Đi ngủ thôi nào!"
                    ticker = "Thời điểm lên giường cùng những giấc mơ"
                    description = "Đã đến giờ đi ngủ một giấc ngon rồi!"
                    text = "Đi ngủ lúc "
                if object.id_type == 3:
                    title = "Thức dậy thôi nào!"
                    ticker = "Thời điểm thức dậy cho hoạt động mới"
                    description = "Đến lúc thức dậy để bắt đầu công việc của bạn!"
                    text = "Thức dậy lúc "
                task = {
                    "alarm_time": object.option_timestamp.strftime(self.str_timestamp),
                    "alarm_type": object.id_type,
                    "title": title,
                    "ticker": ticker,
                    "description": description
                }
                self.timestamp_data = object.option_timestamp
                print(object.option_timestamp.strftime("%a %I:%M %p %d-%m"))
                RqsAlarmSchedule().create_alarm(object.option_timestamp,
                                                title, ticker, description)
                self.save_scheduled_task(task)
                self.activity_alarm = True
                #android_toast("Đã thiết lập thời gian báo thức !")
                self.show_notification_setAlarm(
                    object.option_timestamp, ticker, description, text)
        else:
            RqsAlarmSchedule().cancel_alarm()
            self.save_scheduled_task(self.alarm_default)
            object.option_timestamp = None
            self.timestamp_data = None
            self.activity_alarm = False
            cancel_notification()
            android_toast("Đã hủy báo thức")

    def show_notification_setAlarm(self, time_set, ticker, description, text):
        notify(
            context=mActivity.getApplicationContext(),
            channel_id='RQSRD_ALARM_HEADS_UP',
            text=text + time_set.strftime("%a %d/%m/%Y %I:%M %p"),
            title=ticker,
            name='Alarm',
            description=description,
            extras=[],
            flag='update',
            n_type='head',
            autocancel=False
        )

    def save_scheduled_task(self, task: dict):
        print("---------> save_scheduled_task")
        with open(self.resource_path("assets/scheduled.json"), 'w', encoding='utf-8') as f:
            json.dump(task, f, indent=4)
        print("save_scheduled_task-------> done")

    def load_scheduled_task(self) -> dict:
        print("---------> load_scheduled_task")
        with open(self.resource_path("assets/scheduled.json")) as f:
            task = json.load(f)
            return task

    def actions_filter(self, checkbox, value):
        if not self.activity_alarm:
            if checkbox.parent.id_number in [2, 3]:
                alarm_option = self.root.alarm_option
                if value:
                    alarm_option.option_timestamp = checkbox.parent.option_timestamp
                    alarm_option.id_type = checkbox.parent.id_number
                    alarm_option.twist()
                else:
                    alarm_option.option_timestamp = None
                    alarm_option.id_type = None
                    alarm_option.wobble()


if __name__ == "__main__":
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
    os.environ["root_dir"] = bundle_dir

    Window.soft_input_mode = "below_target"

    AlarmClockApp().run()
