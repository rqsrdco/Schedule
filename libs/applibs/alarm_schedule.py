import json
import logging
from time import sleep
from os import environ
from datetime import datetime
from jnius import cast, autoclass, PythonJavaClass, java_method
from android.runnable import run_on_ui_thread
from android import python_act, activity
from kivy.logger import Logger

mService = autoclass('org.kivy.android.PythonService').mService
mActivity = autoclass("org.kivy.android.PythonActivity").mActivity
context = mActivity.getApplicationContext()

# Autoclass necessary java classes so they can be used in python

PendingIntent = autoclass("android.app.PendingIntent")
AlarmManager = autoclass('android.app.AlarmManager')
Context = autoclass('android.content.Context')
Intent = autoclass("android.content.Intent")
String = autoclass("java.lang.String")
Int = autoclass("java.lang.Integer")
Boolean = autoclass("java.lang.Boolean")
System = autoclass('java.lang.System')
ComponentName = autoclass('android.content.ComponentName')
PackageManager = autoclass('android.content.pm.PackageManager')

# Autoclass our own java class
#AlarmReceiver = autoclass('org.rqsrd.schedule.AlarmReceiver')
RqsAlarmReceiver = autoclass('org.rqsrd.schedule.RqsAlarmReceiver')


class RqsAlarmSchedule:

    def __init__(self):
        # mService.setAutoRestartService(False)
        self.requestCode = 181864

    @run_on_ui_thread
    def enable_receiver(self):
        receiver = ComponentName(context, RqsAlarmReceiver)
        pm = context.getPackageManager()
        pm.setComponentEnabledSetting(
            receiver, PackageManager.COMPONENT_ENABLED_STATE_ENABLED, PackageManager.DONT_KILL_APP)

    @run_on_ui_thread
    def disable_receiver(self):
        receiver = ComponentName(context, RqsAlarmReceiver)
        pm = context.getPackageManager()
        pm.setComponentEnabledSetting(
            receiver, PackageManager.COMPONENT_ENABLED_STATE_DISABLED, PackageManager.DONT_KILL_APP)

    @run_on_ui_thread
    def create_alarm(self, alarm_time, alarm_title, alarm_ticker, alarm_description):
        # enable receiver to receive the alarm
        self.enable_receiver()
        alarmSetTime = int(alarm_time.timestamp()*1000)
        alarmIntent = Intent()
        alarmIntent.setClass(context, RqsAlarmReceiver)
        alarmIntent.setAction("org.rqsrd.schedule.WAKEUP_ALARM")
        alarmIntent.putExtra("title", String(alarm_title))
        alarmIntent.putExtra("ticker", String(alarm_ticker))
        alarmIntent.putExtra("description", String(alarm_description))
        pendingIntent = PendingIntent.getBroadcast(
            context, self.requestCode, alarmIntent, PendingIntent.FLAG_UPDATE_CURRENT)
        alarm = cast(
            AlarmManager, context.getSystemService(Context.ALARM_SERVICE))
        alarm.setExactAndAllowWhileIdle(
            AlarmManager.RTC_WAKEUP, alarmSetTime, pendingIntent)

    @run_on_ui_thread
    def cancel_alarm(self):
        alarmIntent = Intent()
        alarmIntent.setClass(context, RqsAlarmReceiver)
        alarmIntent.setAction("org.rqsrd.schedule.WAKEUP_ALARM")
        pendingIntent = PendingIntent.getBroadcast(
            context, self.requestCode, alarmIntent,
            PendingIntent.FLAG_NO_CREATE
        )
        alarm = cast(
            AlarmManager, context.getSystemService(Context.ALARM_SERVICE))
        if pendingIntent is not None:
            alarm.cancel(pendingIntent)
        self.disable_receiver()

    @run_on_ui_thread
    def dimiss_alarm(self):
        dimiss_alarm_intent = Intent()
        dimiss_alarm_intent.setClass(context, RqsAlarmReceiver)
        dimiss_alarm_intent.setAction("org.rqsrd.schedule.DISMISS_ALARM")
        pendingItent = PendingIntent.getBroadcast(
            context, self.requestCode, dimiss_alarm_intent, PendingIntent.FLAG_ONE_SHOT)
        alarm = cast(AlarmManager, context.getSystemService(
            Context.ALARM_SERVICE))
        alarm.setExact(AlarmManager.RTC_WAKEUP,
                       System.currentTimeMillis(), pendingItent)
