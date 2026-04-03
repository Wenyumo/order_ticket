[app]

title = 北理班车抢票助手
package.name = bitbus

source.dir = .

source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0.0

requirements = python3,kivy,requests,pyjnius

presplash.filename = %(source.dir)s/presplash.png

icon.filename = %(source.dir)s/icon.png

orientation = portrait

fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.archs = arm64-v8a,armeabi-v7a

android.minapi = 21

android.api = 33

android.ndk = 25b

android.accepted_sdk_versions = 33

[buildozer]

log_level = 2

warn_on_root = 1
