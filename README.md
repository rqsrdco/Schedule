AndroidManifest.tmpl.xml
```
<receiver
    android:name=".RqsAlarmReceiver"
    android:enabled="true"
    android:exported="false">
    <intent-filter>
        <action android:name="org.rqsrd.schedule.WAKEUP_ALARM" />
        <action android:name="org.rqsrd.schedule.STOP_SERVICE" />
        <action android:name="android.intent.action.BOOT_COMPLETED"/>
    </intent-filter>
</receiver>

<service 
    android:name=".RunAfterBootService"
    android:exported="false">
</service>
```

buildozer.spec

```
requirements = python3,kivy==master,https://github.com/kivymd/KivyMD/archive/master.zip,pygments,sdl2_ttf==2.0.15,pillow,openssl,urllib3,certifi,requests,chardet,idna,android,plyer,pyjnius,oscpy

android.permissions = INTERNET,WAKE_LOCK,FOREGROUND_SERVICE,USE_FULL_SCREEN_INTENT,VIBRATE,REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,RECEIVE_BOOT_COMPLETED,SET_ALARM,SCHEDULE_EXACT_ALARM,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,BATTERY_STATS,ACCESS_NOTIFICATION_POLICY,ACCESS_MEDIA_LOCATION

services = Rqsrdservice:service/main.py:foreground

p4a.branch = develop

android.add_src = java_src
android.enable_androidx = True
android.release_artifact = apk
```

1. mkdir -p ~/keystores/

```
keytool -genkey -v -keystore ~/keystores/<your-new-key>.keystore -alias <your-key-alias> -keyalg RSA -keysize 2048 -validity 10000
```

==> 

```
keytool -genkey -v -keystore ~/Schedule/keystores/mykeystore.keystore -alias schedule -keyalg RSA -keysize 2048 -validity 365
```

2. PKCS12

```
keytool -importkeystore -srckeystore ~/keystores/<your-new-key>.keystore -destkeystore ~/keystores/<your-new-key>.keystore -deststoretyp
```

==>

```
 keytool -importkeystore -srckeystore ~/Schedule/keystores/mykeystore.keystore -destkeystore ~/Schedule/keystores/mykeystore.keystore -deststoretype pkcs12
```

3. export

```
export P4A_RELEASE_KEYSTORE=~/keystores/<your-new-key>.keystore
export P4A_RELEASE_KEYSTORE_PASSWD="<your-keystore-password>"
export P4A_RELEASE_KEYALIAS_PASSWD="<your-key-alias-password>"
export P4A_RELEASE_KEYALIAS=<your-key-alias>
```

==> 

```
export P4A_RELEASE_KEYSTORE=~/Schedule/keystores/mykeystore.keystore
export P4A_RELEASE_KEYSTORE_PASSWD="schedule"
export P4A_RELEASE_KEYALIAS_PASSWD="schedule"
export P4A_RELEASE_KEYALIAS="schedule"
```

4. cd your-project-folder

```
buildozer -v android release
```

Optimize it

```
 $ ~/.buildozer/android/platform/android-sdk/build-tools/23.0.1/zipalign -v 4 ./bin/Your-App-0.1-release.apk ./bin/Your-App-0.1-release-optimized.apk
```

==>

```
~/Android/Sdk/build-tools/31.0.0/zipalign -v 4 ~/Schedule/bin/schedule-0.3-arm64-v8a-release.apk ~/Schedule/bin/schedule-0.3-arm64-v8a-release-optimized.apk
```

5. adb install & logcat

   
   re-install or update an existing app

```
adb install -r <app name.apk>
adb install -r ~/Schedule/bin/schedule-0.3-arm64-v8a-release.apk
adb install -r ~/Schedule/bin/schedule-0.3-arm64-v8a-release-optimized.apk
```

    install an app on your SD card

```
adb install -s <app name.apk>
```

    logcat

```
adb push <file location path>/sdcard/<folder name>
adb pull /sdcard/<file name><file location path>
adb reboot
adb shell am start -a android.intent.action.BOOT_COMPLETED
adb shell pm list packages

buildozer -v android debug deploy run logcat > my_log.txt
adb logcat org.rqsrd.schedule:D *:S
adb logcat *:S python:D
adb shell logcat | grep org.rqsrd.schedule
adb shell logcat | grep RQSRD_ALARM_RECEIVER
buildozer android adb -- logcat -s python,service,AndroidRuntime
buildozer android adb -- logcat | grep -i python
adb logcat | grep -E "RQSRD_RECEIVER|org.rqsrd.schedule|RQSRD_BOOT_SERVICE"
```