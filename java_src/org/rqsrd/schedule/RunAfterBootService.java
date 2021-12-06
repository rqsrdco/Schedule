package org.rqsrd.schedule;

import android.content.Context;
import android.app.Service;
import android.content.Intent;
import android.app.PendingIntent;
import android.os.IBinder;
import android.util.Log;
import android.os.Build;
import android.provider.Settings;
import java.lang.System;
import android.app.PendingIntent;
import android.app.AlarmManager;
import org.rqsrd.schedule.RqsAlarmReceiver;
import android.content.ComponentName;
import android.content.pm.PackageManager;

import java.io.File;
import java.io.FileReader;
import java.io.BufferedReader;
import java.io.IOException;
import java.lang.StringBuilder;
import org.json.JSONObject;
import org.json.JSONException;

import java.time.LocalDateTime;
import java.time.ZonedDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.text.ParseException;
import java.text.SimpleDateFormat;

public class RunAfterBootService extends Service {
    private static final String TAG = "BOOT_BROADCAST_SERVICE";
    private static final String ALARM_FILE = "scheduled.json";
    private static final String TIME_PATTERN = "E dd/MM/yyyy hh:mm a";

    private static String ALARM_TITLE;
    private static String ALARM_TICKER;
    private static String ALARM_DESCRIPTIONS;
    private static long ALARM_TIME_FIRE;

    public RunAfterBootService() {
    }
    
    @Override
    public IBinder onBind(Intent intent) {
        // TODO: Return the communication channel to the service.
        return null;
    }

    private void checkScheduledAlarm(Context context) {
        //String filesD = "/data/data/org.rqsrd.schedule/files/";
        //String fileName = "/app/assets/scheduled.json";
        Log.d(TAG, "checkScheduledAlarm");
        File filesDir = context.getFilesDir();
        File assetsDir = new File(filesDir + File.separator + "app" + File.separator, "assets");
        File scheduledFile = new File(assetsDir, ALARM_FILE);
        if (!scheduledFile.exists()) {
            ALARM_TIME_FIRE = 0;
            return;
        } else {
            try{
                BufferedReader br = new BufferedReader(new FileReader(scheduledFile));
                StringBuilder sb = new StringBuilder();
                String line = br.readLine();
                while (line != null) {
                    sb.append(line);
                    line = br.readLine();
                }
                br.close();
                String jsonString = sb.toString();
                JSONObject json = new JSONObject(jsonString);
                String alarmTime = json.getString("alarm_time");
                if (alarmTime == null || alarmTime.isEmpty() || alarmTime.trim().equals("")) {
                    Log.d(TAG, "alarm time is empty");
                    ALARM_TIME_FIRE = 0;
                    return;
                } else {
                    ALARM_TITLE = json.getString("title");
                    ALARM_TICKER = json.getString("ticker");
                    ALARM_DESCRIPTIONS = json.getString("description");
                    DateTimeFormatter formatter = DateTimeFormatter.ofPattern(TIME_PATTERN);
                    LocalDateTime dateTime = LocalDateTime.parse(alarmTime, formatter);
                    long dateTimeMillis = dateTime.atZone(ZoneId.systemDefault()).toInstant().toEpochMilli();
                    ALARM_TIME_FIRE = dateTimeMillis;
                    Log.d(TAG, String.valueOf(dateTimeMillis));
                }
            } catch (IOException e) {
                Log.d(TAG, "IOException: " + e.getMessage());
                ALARM_TIME_FIRE = 0;
            } catch (JSONException e) {
                Log.d(TAG, "JSONException: " + e.getMessage());
                ALARM_TIME_FIRE = 0;
            }
        }
    }
    
    private void rescheduleTask(Context context) {
        Log.d(TAG, "rescheduleTask");
        Intent intent = new Intent(context, RqsAlarmReceiver.class);
        intent.setAction("org.rqsrd.schedule.WAKEUP_ALARM");
        intent.putExtra("title", ALARM_TITLE);
        intent.putExtra("ticker", ALARM_TICKER);
        intent.putExtra("description", ALARM_DESCRIPTIONS);
        PendingIntent pendingIntent = PendingIntent.getBroadcast(context, 181864, intent,
                PendingIntent.FLAG_UPDATE_CURRENT);
        AlarmManager alarmManager = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        alarmManager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, ALARM_TIME_FIRE,
                pendingIntent);
        //------------------
        //PendingIntent sender = PendingIntent.getBroadcast(context, 0, intent, 0);
        //AlarmManager am = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        //Intent showIntent = new Intent(context, RqsAlarmReceiver.class);
        //PendingIntent showOperation = PendingIntent.getActivity(context, 0, showIntent, PendingIntent.FLAG_UPDATE_CURRENT);
        //AlarmManager.AlarmClockInfo alarmClockInfo = new AlarmManager.AlarmClockInfo(ALARM_TIME_FIRE, showOperation);
        //am.setAlarmClock(alarmClockInfo, sender);
    }

    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(TAG, "onCreate");
        ALARM_TITLE = "";
        ALARM_TICKER = "";
        ALARM_DESCRIPTIONS = "";
        ALARM_TIME_FIRE = 0;
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId){
        Log.d(TAG, "onStartCommand");
        checkScheduledAlarm(this);
        if(ALARM_TIME_FIRE != 0) {
            rescheduleTask(this);
        } else {
            Log.d(TAG, "No alarm scheduled");
        }
        return START_NOT_STICKY;
        //return super.onStartCommand(intent, flags, startId);
    }
    
    @Override
    public void onDestroy() {
        super.onDestroy();
        Log.d(TAG, "onDestroy: Called");
    }
}