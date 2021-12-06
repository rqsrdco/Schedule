package org.rqsrd.schedule;

import android.content.BroadcastReceiver;
import android.content.Intent;
import android.content.Context;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationCompat.Action;
import androidx.core.app.NotificationManagerCompat;
import android.app.Notification;
import android.os.Build;
import android.media.RingtoneManager;
import android.net.Uri;
import android.media.AudioAttributes;
import org.rqsrd.schedule.R;
import java.lang.Math;
import android.app.PendingIntent;
import org.kivy.android.PythonActivity;
import android.util.Log;
import android.os.Bundle;
import android.widget.Toast;

import android.app.AlarmManager;
import android.app.ActivityManager;
import java.lang.Class;
import android.os.PowerManager;

import org.rqsrd.schedule.RunAfterBootService;
import org.rqsrd.schedule.ServiceRqsrdservice;


public class RqsAlarmReceiver extends BroadcastReceiver {

    public static final String TAG = "RQSRD_ALARM_RECEIVER";
    public static final String CHANNEL_ID = "REACTION_ALARM";
    public static final int NOTIFICATION_ID = 11235813;

    private PowerManager.WakeLock mWakeLock;

    private void createNotificationChannel(Context context) {

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            Uri sound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM);

            AudioAttributes att = new AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_ALARM)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                    .build();

            CharSequence name = "RQSRD_ALARM";
            String description = "It's time";
            int importance = NotificationManager.IMPORTANCE_HIGH;
            NotificationChannel channel = new NotificationChannel(CHANNEL_ID, name, importance);
            channel.setDescription(description);
            channel.setSound(sound, att);
            channel.enableLights(true);
            channel.enableVibration(true);
            NotificationManager notificationManager = context.getSystemService(NotificationManager.class);
            notificationManager.createNotificationChannel(channel);
        }
    }
    
    private void sendNotification(Context context, String title, String ticker, String description) {
        Intent fullScreenIntent = new Intent(context, PythonActivity.class);
        fullScreenIntent.putExtra("alarmIsOn", true);
        PendingIntent fullScreenPendingIntent = PendingIntent.getActivity(context, 654321, fullScreenIntent,
                PendingIntent.FLAG_UPDATE_CURRENT);

        Uri uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM);
        //int notification_id = (int)(Math.random()*(8000-1+1)+1);

        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, CHANNEL_ID)
                .setSmallIcon(context.getApplicationInfo().icon).setContentTitle(title).setContentText(description)
                .setStyle(new NotificationCompat.BigTextStyle().bigText(description)).setTicker(ticker)
                .setVibrate(new long[] { 500, 500, 500, 500, 500, 500 }).setSound(uri).setAutoCancel(true)
                .setVisibility(NotificationCompat.VISIBILITY_PUBLIC).setOnlyAlertOnce(false)
                .setPriority(NotificationCompat.PRIORITY_HIGH).setCategory(NotificationCompat.CATEGORY_ALARM)
                .setFullScreenIntent(fullScreenPendingIntent, true);

        NotificationManagerCompat notificationManager = NotificationManagerCompat.from(context);
        notificationManager.notify(NOTIFICATION_ID, builder.build());
    }

    /* Create an repeat Alarm that will invoke the background service for each execution time.*/
    private void startServiceByAlarm(Context context, Class<?> serviceClass)
    {
        // Get alarm manager.
        AlarmManager alarmManager = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        // Create intent to invoke the background service.
        Intent intent = new Intent(context, serviceClass);
        PendingIntent pendingIntent = PendingIntent.getService(context, 0, intent, PendingIntent.FLAG_UPDATE_CURRENT);
        long startTime = System.currentTimeMillis();
        long intervalTime = 60 * 1000;
        String message = "Start service use repeat alarm. ";
        Toast.makeText(context, message, Toast.LENGTH_LONG).show();
        Log.d(TAG, message);
        // Create repeat alarm.
        alarmManager.setRepeating(AlarmManager.RTC_WAKEUP, startTime, intervalTime, pendingIntent);
    }

    private void startServiceDirectly(Context context, Class<?> serviceClass) {
        Log.d(TAG, "Start service directly.");
        Intent startServiceIntent = new Intent(context, serviceClass);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.startForegroundService(startServiceIntent);
        } else {
            context.startService(startServiceIntent);
        }
    }
    
    private boolean isServiceRunning(Context context, Class<?> serviceClass) {
        ActivityManager manager = (ActivityManager) context.getSystemService(Context.ACTIVITY_SERVICE);
        for (ActivityManager.RunningServiceInfo service : manager.getRunningServices(Integer.MAX_VALUE)) {
            if (serviceClass.getName().equals(service.service.getClassName())) {
                return true;
            }
        }
        return false;
    }

    @Override
    public void onReceive(Context context, Intent intent) {
        Log.d(TAG, "-----------------------------------");
        if (intent != null) {
            String action = intent.getAction();
            if (action != null) {
                if (action.equals("org.rqsrd.schedule.WAKEUP_ALARM")) {
                    Log.d(TAG, "Received wakeup alarm.");
                    PowerManager pm = (PowerManager) context.getSystemService(Context.POWER_SERVICE);
                    mWakeLock = pm.newWakeLock(PowerManager.SCREEN_BRIGHT_WAKE_LOCK |
                            PowerManager.ACQUIRE_CAUSES_WAKEUP |
                            PowerManager.ON_AFTER_RELEASE, "RqsAlarmReceiver");
                    mWakeLock.acquire();
                    String title = intent.getStringExtra("title");
                    String ticker = intent.getStringExtra("ticker");
                    String description = intent.getStringExtra("description");
                    this.createNotificationChannel(context);
                    this.sendNotification(context, title, ticker, description);
                }
                if (action.equals("org.rqsrd.schedule.DISMISS_ALARM")) {
                    Log.d(TAG, "Received dismiss alarm.");
                    if (mWakeLock != null) {
                        mWakeLock.release();
                    }
                    if (isServiceRunning(context, RunAfterBootService.class)) {
                        Log.d(TAG, "isServiceRunning");
                        try {
                            Log.d(TAG, "Call Stopping RunAfterBootService");
                            //context.stopService(new Intent(context, RunAfterBootService.class));
                        } catch (Exception e) {
                            Log.e(TAG, "Error stopping RunAfterBootService");
                        }
                    }
                }
                if (action.equals(Intent.ACTION_BOOT_COMPLETED)) {
                    Log.d(TAG, "Received boot completed.");
                    this.startServiceDirectly(context, RunAfterBootService.class);
                    try{
                        Intent ix = new Intent(context, ServiceRqsrdservice.class);
                        String argument = context.getFilesDir().getAbsolutePath() + "/app";
                        ix.putExtra("androidPrivate", context.getFilesDir().getAbsolutePath());
                        ix.putExtra("androidArgument", argument);
                        ix.putExtra("serviceTitle", "Reaction");
                        ix.putExtra("serviceDescription", "Rqsrdservice");
                        ix.putExtra("serviceEntrypoint", "service/main.py");
                        ix.putExtra("pythonName", "Rqsrdservice");
                        ix.putExtra("pythonHome", argument);
                        ix.putExtra("pythonPath", argument + ":" + argument + "/lib");
                        ix.putExtra("pythonServiceArgument", "wakeup");
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                            ix.putExtra("serviceStartAsForeground", "true");
                            context.startForegroundService(ix);
                        } else {
                            ix.putExtra("serviceStartAsForeground", "false");
                            context.startService(ix);
                        }
                    }catch(Exception e){
                        Log.e(TAG, e.getMessage());
                        Log.d(TAG, e.getMessage());
                    }
                }
            }
        }
        Log.d(TAG, "-----------------------------------");
    }
}