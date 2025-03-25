import os
import sys
import subprocess
import webbrowser

def is_android():
    """تحقق إذا كان النظام يعمل على أندرويد"""
    android_indicators = [
        "/system/build.prop",          # ملف خاص بأندرويد
        "/system/bin/pm",              # أداة إدارة الحزم
        "ANDROID_ROOT" in os.environ,  # متغير بيئة أندرويد
        "ANDROID_DATA" in os.environ,
        hasattr(sys, 'getandroidapilevel')  # في بعض بيئات بايثون لأندرويد
    ]
    return any(android_indicators)

def get_android_version():
    """الحصول على إصدار أندرويد بدون صلاحيات root"""
    methods = [
        lambda: subprocess.getoutput("getprop ro.build.version.release"),
        lambda: read_android_file("/system/build.prop", "ro.build.version.release="),
        lambda: os.environ.get("ANDROID_VERSION", "")
    ]
    
    for method in methods:
        try:
            result = method().strip()
            if result: return result
        except:
            continue
    return "غير معروف"

def read_android_file(file_path, key):
    """قراءة ملف أندرويد للبحث عن معلومات محددة"""
    try:
        with open(file_path, 'r', encoding='latin-1') as f:
            for line in f:
                if line.startswith(key):
                    return line.split("=")[1].strip()
    except:
        return ""

def get_system_info():
    """الحصول على معلومات النظام الأساسية"""
    info = {
        'system': os.name,
        'platform': sys.platform,
        'uname': os.uname() if hasattr(os, 'uname') else None
    }
    return info

def redirect_to_company_site(os_type):
    """توجيه المستخدم إلى موقع الشركة حسب نظام التشغيل"""
    company_sites = {
        'android': 'https://www.google.com/',
        'windows': 'https://www.example.com/windows',
        'macos': 'https://www.example.com/macos',
        'linux': 'https://www.example.com/linux',
        'ios': 'https://www.example.com/ios',
        'default': 'https://www.example.com'
    }
    
    url = company_sites.get(os_type.lower(), company_sites['default'])
    print(f"جاري توجيهك إلى موقع الشركة لنظام {os_type}...")
    webbrowser.open(url)

def detect_os():
    print("=== نظام التشغيل الخاص بك ===")
    
    system_info = get_system_info()
    os_type = "غير معروف"
    
    if is_android():
        version = get_android_version()
        print("- نظام التشغيل: Android")
        print(f"- الإصدار: {version}")
        os_type = "android"
        
        if system_info['uname']:
            print(f"- إصدار النواة: {system_info['uname'].release}")
            print(f"- معمارية الجهاز: {system_info['uname'].machine}")
    
    elif system_info['platform'] == 'win32':
        print("- نظام التشغيل: Windows")
        print(f"- الإصدار: {sys.getwindowsversion().major}.{sys.getwindowsversion().minor}")
        os_type = "windows"
    
    elif system_info['platform'] == 'darwin':
        # التمييز بين macOS و iOS
        if 'iPhone' in system_info['uname'].machine or 'iPad' in system_info['uname'].machine:
            print("- نظام التشغيل: iOS")
            os_type = "ios"
        else:
            print("- نظام التشغيل: macOS")
            os_type = "macos"
        
        if system_info['uname']:
            print(f"- إصدار النواة: {system_info['uname'].release}")
    
    elif system_info['platform'].startswith('linux'):
        print("- نظام التشغيل: Linux")
        os_type = "linux"
        if system_info['uname']:
            print(f"- إصدار النواة: {system_info['uname'].release}")
            print(f"- معمارية الجهاز: {system_info['uname'].machine}")
    
    else:
        print(f"- نظام غير معروف: {system_info['platform']}")
    
    print("=========================")
    return os_type

if __name__ == "__main__":
    detected_os = detect_os()
    redirect_to_company_site(detected_os)
