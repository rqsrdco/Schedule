from random import choice

from kivymd.uix.behaviors import FakeCircularElevationBehavior
from kivymd.uix.behaviors.magic_behavior import MagicBehavior
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.app import MDApp
from kivy import properties as P
from kivy.clock import Clock, mainthread
from kivy.utils import platform
from kivy.metrics import dp
from kivy.animation import Animation
from libs.applibs.load_kv_file import load_kv
from datetime import datetime, timedelta, date

if platform == 'android':
    from android import activity
    from libs.applibs.notification import cancel_notification

load_kv(file_name="alarm_screen.kv")


class AlarmScreen(MDScreen):
    current_datetime = P.StringProperty("")
    dateTime_picker = P.ObjectProperty(None, allownone=True)
    op4h44m_284 = P.ObjectProperty()
    op6h14m_374 = P.ObjectProperty()
    op7h44m_464 = P.ObjectProperty()
    op9h14m_554 = P.ObjectProperty()

    alarm_option = P.ObjectProperty()

    def __init__(self, **kwargs):
        self.name = "alarm"
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        Clock.schedule_once(self.init_guide, 1)

    def init_guide(self, dt):
        self.ids.grv_list_calc.clear_widgets()
        self.ids.grv_list_calc.add_widget(
            OptionAlarm(
                size=(dp(500), dp(99)),
                id_number=1,
                text="Chọn mốc thời gian bạn muốn báo thức dậy, tôi sẽ đưa ra những gợi ý tối ưu cho mốc thời gian bạn nên đi ngủ, để thức dậy sảng khoái, tràn đầy năng lượng. Hoặc bạn lựa chọn những mốc thời gian nên thức dậy nếu đi ngủ ngay bây giờ bên dưới !"
            )
        )

    def on_pre_leave(self, *args):
        super().on_pre_leave(*args)
        print("AlarmScreen.on_pre_leave")
        Clock.unschedule(self.update_current_datetime_guest)

    def update_current_datetime_guest(self, dt):
        current_datetime = datetime.now()
        # self.current_datetime = current_datetime.strftime(
        #    "%a %d/%m/%Y %I:%M:%S %p")
        self.op4h44m_284.option_timestamp = current_datetime + \
            timedelta(hours=4, minutes=44)
        self.op6h14m_374.option_timestamp = current_datetime + \
            timedelta(hours=6, minutes=14)
        self.op7h44m_464.option_timestamp = current_datetime + \
            timedelta(hours=7, minutes=44)
        self.op9h14m_554.option_timestamp = current_datetime + \
            timedelta(hours=9, minutes=14)

    def add_alarm(self):
        if not self.app.date_dialog:
            self.app.init_date_picker()
        if not self.app.time_dialog:
            self.app.init_time_picker()
        self.app.date_dialog.bind(on_save=self.on_date_picker_save)
        self.app.date_dialog.open()

    def on_date_picker_save(self, instance, value, date_range):
        self.dateTime_picker = datetime(
            day=value.day, month=value.month, year=value.year,
        )
        self.app.time_dialog.bind(time=self.on_time_picker_save)
        self.app.time_dialog.open()

    def on_time_picker_save(self, instance, value):
        self.dateTime_picker = self.dateTime_picker.replace(
            hour=value.hour, minute=value.minute)

    def on_dateTime_picker(self, instance, value):
        current_timestamp = datetime.now()
        if value > current_timestamp:
            results = []
            for op in self.app.reaction_value:
                val = value - timedelta(
                    hours=op["hours"], minutes=op["minutes"]
                )
                if val >= current_timestamp:
                    item = OptionAlarm(
                        option_timestamp=val,
                        size=(dp(180), dp(99)),
                        id_number=2,
                        text="Bạn nên đi ngủ vào lúc [b][color=c90533]%s[/color][/b]" % val.strftime(
                            "%a %d/%m/%Y %I:%M %p")
                    )
                    results.append(item)
            if results == []:
                self.ids.lbl_calc_time.text = "[color=ffffff]Xin chọn mốc thời gian khác lớn hơn ![/color]"
                self.ids.grv_list_calc.clear_widgets()
                self.ids.grv_list_calc.add_widget(OptionAlarm(
                    size=(dp(500), dp(99)),
                    id_number=1,
                    text="Chọn mốc thời gian bạn muốn báo thức dậy, tôi sẽ đưa ra những gợi ý tối ưu cho mốc thời gian bạn nên đi ngủ, để thức dậy sảng khoái, tràn đầy năng lượng. Hoặc bạn lựa chọn những mốc thời gian nên thức dậy nếu đi ngủ ngay bây giờ bên dưới !"
                ))
            else:
                self.ids.lbl_calc_time.text = "Để thức dậy lúc [b][color=c90533]%s[/color][/b]" % self.dateTime_picker.strftime(
                    "%a %d/%m/%Y %I:%M %p")
                self.ids.grv_list_calc.clear_widgets()
                for item in results:
                    self.ids.grv_list_calc.add_widget(item)
        else:
            self.ids.lbl_calc_time.text = "[color=ffffff]Bạn chưa chọn mốc thời gian để thức dậy ?[/color]"
            self.ids.grv_list_calc.clear_widgets()
            self.ids.grv_list_calc.add_widget(OptionAlarm(
                size=(dp(500), dp(99)),
                id_number=1,
                text="Chọn mốc thời gian bạn muốn báo thức dậy, tôi sẽ đưa ra những gợi ý tối ưu cho mốc thời gian bạn nên đi ngủ, để thức dậy sảng khoái, tràn đầy năng lượng. Hoặc bạn lựa chọn những mốc thời gian nên thức dậy nếu đi ngủ ngay bây giờ bên dưới !"
            ))


class OptionAlarm(MDCard, FakeCircularElevationBehavior, MagicBehavior):
    text = P.StringProperty("Chưa chọn thời gian báo thức")
    option_timestamp = P.ObjectProperty(allownone=True)
    id_number = P.NumericProperty()
    id_type = P.NumericProperty(allownone=True)

    def on_option_timestamp(self, instance, value):
        if value:
            if self.id_number == 0:
                self.text = "Báo thức lúc " + \
                    self.option_timestamp.strftime("%a %d/%m/%Y %I:%M %p")
            elif self.id_number == 3:
                self.text = "Thức dậy vào lúc " + \
                    self.option_timestamp.strftime("%a %d/%m/%Y %I:%M %p")
            elif self.id_number == 2:
                self.text = "Bạn nên đi ngủ vào lúc " + \
                    self.option_timestamp.strftime("%a %d/%m/%Y %I:%M %p")
        else:
            if self.id_number == 0:
                self.text = "Chưa chọn thời gian báo thức"
