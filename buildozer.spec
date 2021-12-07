[app]

# (str) Title of your application

title = Reaction

package.name = schedule

package.domain = org.rqsrd

source.dir = .

source.include_exts = py,png,jpg,kv,atlas,ttf,json

source.include_patterns = assets/*

source.exclude_exts = spec, sh, md

source.exclude_dirs = tests, bin, venv

# (str) Application versioning (method 2)

version.regex = __version__ = ['"](.*)['"]

version.filename = %(source.dir)s/main.py

# (list) Application requirements

# comma separated e.g. requirements = sqlite3,kivy

requirements = python3,kivy==master,https://github.com/kivymd/KivyMD/archive/master.zip,pygments,sdl2_ttf==2.0.15,pillow,openssl,urllib3,certifi,requests,chardet,idna,android,plyer,pyjnius,oscpy

presplash.filename = %(source.dir)s/assets/icons/presplash.png

# (str) Icon of the application

icon.filename = %(source.dir)s/assets/icons/logo.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)

orientation = portrait

services = Rqsrdservice:service/main.py
# change the major version of python used by the app

osx.python_version = 3

# Kivy version to use

osx.kivy_version = 1.9.1


fullscreen = 0

#android.apptheme = "@style/Theme.AppCompat"

# Supported formats are: #RRGGBB #AARRGGBB or one of the following names:

# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray,

# darkgray, grey, lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy,

# olive, purple, silver, teal.

android.presplash_color = #282a43

# Lottie files can be created using various tools, like Adobe After Effect or Synfig.

android.presplash_lottie = "assets/lotties/social.json"

# (list) Permissions

android.permissions = INTERNET,WAKE_LOCK,FOREGROUND_SERVICE,USE_FULL_SCREEN_INTENT,VIBRATE,REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,RECEIVE_BOOT_COMPLETED,SET_ALARM,SCHEDULE_EXACT_ALARM,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,BATTERY_STATS,ACCESS_NOTIFICATION_POLICY,ACCESS_MEDIA_LOCATION

# (int) Target Android API, should be as high as possible.

android.api = 30

#android.minapi = 26

#android.ndk_api = 26

# (bool) If True, then skip trying to update the Android sdk

# This can be useful to avoid excess Internet downloads or save time

# when an update is due and you just want to test/build your package

android.skip_update = False

# (bool) If True, then automatically accept SDK license

# agreements. This is intended for automation only. If set to False,

# the default, you will be shown the license when first running

# buildozer.

android.accept_sdk_license = True
# (list) List of Java files to add to the android project (can be java or a

# directory containing the files)

#android.add_src =
android.add_src = java_src

# (list) Gradle dependencies to add


android.gradle_dependencies = androidx.work:work-runtime:2.2.0

# (bool) Enable AndroidX support. Enable when 'android.gradle_dependencies'

# contains an 'androidx' package, or any package from Kotlin source.

# android.enable_androidx requires android.api >= 28

android.enable_androidx = True
# (list) Java classes to add as activities to the manifest.

android.wakelock = True
#android.add_activities = org.rqsrd.kivyalarm.ReScheduleActivity


# (str) Android logcat filters to use

android.logcat_filters = *:S python:D

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64

android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)

android.allow_backup = True

#android.private_storage = True
#android.entrypoint = org.rqsrd.kivyalarm.BitDustActivity
#android.activity_class_name = org.rqsrd.kivyalarm.BitDustActivity
#android.service_class_name = org.rqsrd.kivyalarm.BitDustService
#android.manifest.launch_mode = singleTask
#android.add_aars = support-compat-27.0.0.aar
#android.extra_manifest_application_arguments = ./etc/extra_manifest_application_arguments.xml

# (str) python-for-android branch to use, defaults to master

p4a.branch = develop

android.release_artifact = apk

# (str) Bootstrap to use for android builds

p4a.bootstrap = sdl2

#p4a.source_dir = ~/python-for-android/
#p4a.local_recipes = ./recipes/

ios.kivy_ios_url = https://github.com/kivy/kivy-ios

ios.kivy_ios_branch = master

# Another platform dependency: ios-deploy

# Uncomment to use a custom checkout

#ios.ios_deploy_dir = ../ios_deploy

# Or specify URL and branch

ios.ios_deploy_url = https://github.com/phonegap/ios-deploy

ios.ios_deploy_branch = 1.10.0

# (bool) Whether or not to sign the code

ios.codesign.allowed = false

[buildozer]



# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))

log_level = 2
# (int) Display warning if buildozer is run as root (0 = False, 1 = True)

warn_on_root = 1
