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
    from android import activity
    from android.runnable import run_on_ui_thread
    from jnius import autoclass, cast, JavaException
    from android.config import ACTIVITY_CLASS_NAME, SERVICE_CLASS_NAME
    from android.storage import primary_external_storage_path
    from android.permissions import request_permissions, Permission

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    mActivity = PythonActivity.mActivity
    Uri = autoclass('android.net.Uri')
    Intent = autoclass('android.content.Intent')
    Context = autoclass('android.content.Context')
    Settings = autoclass('android.provider.Settings')
    PowerManager = autoclass('android.os.PowerManager')
    PackageManager = autoclass('android.content.pm.PackageManager')
    String = autoclass('java.lang.String')

    from libs.applibs.toast import android_toast
    from libs.applibs.vibrator import AndroidVibrator
    from libs.applibs.alarm_schedule import RqsAlarmSchedule
    from libs.applibs.notification import cancel_notification, notify

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
    pending_alarm = False

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
        ret = request_permissions(list_permissions or APP_STARTUP_PERMISSIONS)

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

    def on_timestamp_data(self, instance, value):
        if value is not None:
            self.root.alarm_option.ids.lbl_time.font_size = sp(18)
            Clock.schedule_interval(self.show_time_remain, 1)
        else:
            self.root.alarm_option.ids.lbl_time.font_size = sp(14)
            Clock.unschedule(self.show_time_remain)

    def show_time_remain(self, dt):
        now = datetime.now()
        if self.timestamp_data > now:
            timeDelta = self.timestamp_data - now
            hours, remainder = divmod(timeDelta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            _text = "C??n "
            if hours > 0:
                _text += "%s gi??? " % str(hours).zfill(2)
            if minutes > 0:
                _text += "%s ph??t " % str(minutes).zfill(2)
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

    def on_start(self):
        if platform == 'android':
            self.request_app_permissions()
            self.start_service()
            activity.bind(on_new_intent=self.on_new_intent)
            self.on_new_intent(mActivity.getIntent())
        self.load_alarm_scheduled()
        Clock.schedule_interval(self.root.update_current_datetime_guest, 1)

    def on_pause(self):
        Clock.unschedule(self.root.update_current_datetime_guest)
        self.stop_service()
        return True

    def on_resume(self):
        self.start_service()
        Clock.schedule_interval(self.root.update_current_datetime_guest, 1)

    def on_stop(self):
        self.stop_service()
        Clock.unschedule(self.root.update_current_datetime_guest)

    def on_new_intent(self, intent):
        if intent.getStringExtra("exit") == "exit":
            self.handle_exit_app()
        self.pending_alarm = intent.getBooleanExtra("alarmIsOn", False)
        if self.pending_alarm:
            self.root.alarm_option.option_timestamp = self.timestamp_data

    def load_alarm_scheduled(self):
        task = self.load_scheduled_task()
        if (not(task.get("alarm_time") and task.get("alarm_time").strip())):
            self.root.alarm_option.option_timestamp = None
        else:
            alarm_datetime = datetime.strptime(
                task.get("alarm_time"),
                self.str_timestamp
            )
            now = datetime.now()
            if alarm_datetime > now:
                self.root.alarm_option.option_timestamp = alarm_datetime
                self.timestamp_data = alarm_datetime
                self.activity_alarm = True
            else:
                self.root.alarm_option.option_timestamp = alarm_datetime
                self.activity_alarm = True

    def set_alarm(self, object):
        if not self.activity_alarm:
            if object.option_timestamp is None:
                android_toast("Ch??a ch???n m???c th???i gian b??o th???c ?")
            else:
                if object.id_type == 2:
                    title = "??i ng??? th??i n??o!"
                    ticker = "Th???i ??i???m l??n gi?????ng c??ng nh???ng gi???c m??"
                    description = "???? ?????n gi??? ??i ng??? m???t gi???c ngon r???i!"
                    text = "??i ng??? l??c "
                if object.id_type == 3:
                    title = "Th???c d???y th??i n??o!"
                    ticker = "Th???i ??i???m th???c d???y cho ho???t ?????ng m???i"
                    description = "?????n l??c th???c d???y ????? b???t ?????u c??ng vi???c c???a b???n!"
                    text = "Th???c d???y l??c "
                task = {
                    "alarm_time": object.option_timestamp.strftime(self.str_timestamp),
                    "alarm_type": object.id_type,
                    "title": title,
                    "ticker": ticker,
                    "description": description
                }
                self.timestamp_data = object.option_timestamp
                RqsAlarmSchedule().create_alarm(object.option_timestamp,
                                                title, ticker, description)
                self.save_scheduled_task(task)
                self.activity_alarm = True
                self.show_notification_setAlarm(
                    object.option_timestamp, ticker, description, text)
                self.set_window_flags()
        else:
            if self.pending_alarm:
                RqsAlarmSchedule().dimiss_alarm()
                self.pending_alarm = False
            else:
                RqsAlarmSchedule().cancel_alarm()
            self.save_scheduled_task(self.alarm_default)
            object.option_timestamp = None
            self.timestamp_data = None
            self.activity_alarm = False
            cancel_notification()
            self.reset_window_flags()
            android_toast("???? h???y b??o th???c")

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
        with open(self.resource_path("assets/scheduled.json"), 'w', encoding='utf-8') as f:
            json.dump(task, f, indent=4)

    def load_scheduled_task(self) -> dict:
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

    def _get_audiomanager(self):
        if not hasattr(self, 'audiomanager'):
            if platform == 'android':
                context = mActivity.getApplicationContext()
                Context = autoclass('android.content.Context')
                self.audiomanager = context.getSystemService(
                    Context.AUDIO_SERVICE)
        return self.audiomanager

    def _get_ringtone(self):
        if not hasattr(self, 'ringtone'):
            if platform == 'android':
                RingtoneManager = autoclass('android.media.RingtoneManager')
                AudioManager = autoclass('android.media.AudioManager')
                u = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
                self.ringtone = RingtoneManager.getRingtone(
                    mActivity.getApplicationContext(), u)
                self.ringtone.setStreamType(AudioManager.STREAM_ALARM)
        return self.ringtone

    def _get_vibrator(self):
        if not hasattr(self, 'vibrator') and platform == 'android':
            Context = autoclass('android.content.Context')
            self.vibrator = mActivity.getApplicationContext().getSystemService(
                Context.VIBRATOR_SERVICE)
        return self.vibrator

    @run_on_ui_thread
    def set_window_flags(self):
        LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
        mActivity.getWindow().addFlags(LayoutParams.FLAG_KEEP_SCREEN_ON)

    @run_on_ui_thread
    def reset_window_flags(self):
        LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
        mActivity.getWindow().clearFlags(LayoutParams.FLAG_KEEP_SCREEN_ON)

    def fire_alarm(self):
        if platform == 'android':
            AudioManager = autoclass('android.media.AudioManager')
            am = self._get_audiomanager()
            am.setStreamVolume(AudioManager.STREAM_ALARM,
                               am.getStreamMaxVolume(
                                   AudioManager.STREAM_ALARM),
                               0)
            self.ringer_mode = am.getRingerMode()
            am.setRingerMode(AudioManager.RINGER_MODE_NORMAL)
            self._get_ringtone().play()
            self._get_vibrator().vibrate([0, 500, 500], 1)

    def stop_alarm(self):
        assert hasattr(self, 'ringer_mode')
        self._get_ringtone().stop()
        if platform == 'android':
            AudioManager = autoclass('android.media.AudioManager')
            am = self._get_audiomanager()
            am.setStreamVolume(AudioManager.STREAM_ALARM,
                               am.getStreamMaxVolume(
                                   AudioManager.STREAM_ALARM),
                               0)
            am.setRingerMode(self.ringer_mode)
            # am.setRingerMode(AudioManager.RINGER_MODE_SILENT)
            self._get_vibrator().cancel()
        # self.reset_window_flags()


if __name__ == "__main__":
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
    os.environ["root_dir"] = bundle_dir

    Window.soft_input_mode = "below_target"

    AlarmClockApp().run()
