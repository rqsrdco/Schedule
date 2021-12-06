AndroidManifest.tmpl.xml
```
<receiver
    android:name=".RqsAlarmReceiver"
    android:enabled="true"
    android:exported="false">
    <intent-filter>
        <action android:name="org.rqsrd.schedule.WAKEUP_ALARM" />
        <action android:name="org.rqsrd.schedule.DISMISS_ALARM" />
        <action android:name="android.intent.action.BOOT_COMPLETED"/>
    </intent-filter>
</receiver>

<service android:name=".RunAfterBootService" />
```

You need to create the key

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
 $ ~/.buildozer/android/platform/android-sdk-20/build-tools/23.0.1/zipalign -v 4 ./bin/Your-App-0.1-release.apk ./bin/Your-App-0.1-release-optimized.apk
```

logcat

```
adb shell am start -a android.intent.action.BOOT_COMPLETED

buildozer -v android debug deploy run logcat > my_log.txt

adb shell pm list packages

adb logcat org.rqsrd.schedule:D *:S

adb logcat *:S python:D

adb shell logcat | grep org.rqsrd.schedule
adb shell logcat | grep RQSRD_ALARM_RECEIVER

buildozer android adb -- logcat -s python,service,AndroidRuntime

buildozer android adb -- logcat | grep -i python

adb logcat | grep -E "python|RQSRD_ALARM_RECEIVER|org.rqsrd.schedule|BOOT_BROADCAST_SERVICE"
```