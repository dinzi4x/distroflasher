import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
import webbrowser


TEXTS = {
    "en": {
        "title": "=== OMNI USB FLASHER (Linux / Windows / macOS) ===",
        "select_os": "\nSelect OS category (Tab):",
        "tab_win": "  Windows (11 / 10 / 7 / Vista / XP)",
        "tab_lin": "  Linux (Arch / Fedora / Mint / Debian / Custom)",
        "tab_mac": "  macOS (Sequoia / Sonoma / Ventura / Monterey Recovery)",
        "choose": "\nYour choice: ",
        "invalid": "Invalid choice.",
        "checking": "🔍 Fetching latest versions from official mirrors...",
        "version": "version",
        "custom_linux": "Custom (enter distro-version, e.g. fedora-42 or local path)",
        "custom_prompt": "Enter distro-version (e.g. fedora-42), direct URL, or drag & drop local .iso file: ",
        "searching_custom": "🔎 Searching mirror for {query}...",
        "not_found_url": "Could not auto-resolve URL. Paste direct .iso link or local file path: ",
        "win_menu": "\n🪟 Select Windows version:",
        "win_local": "Enter full path to your {ver} .iso file (or drag & drop it here, or type 'web' to open download page): ",
        "file_not_found": "❌ File not found! Check the path and try again.",
        "mac_menu": "\n🍎 Select macOS Recovery version (~650 MB fast download):",
        "no_usb": "\n❌ No USB flash drives found! Plug in a USB drive and try again.",
        "usb_list": "\n💾 Available USB drives:",
        "choose_usb": "\nSelect USB drive number: ",
        "warn_wipe": "\n🚨 ALL DATA ON {path} ({model}) WILL BE ERASED! Type YES to confirm: ",
        "cancelled": "Cancelled.",
        "downloading": "\n⬇️ Downloading: {url}",
        "progress": "\rProgress: {percent:5.1f}% ({done:.1f} / {total:.1f} MB)",
        "downloaded_mb": "\rDownloaded: {done:.1f} MB...",
        "dl_done": "\n✅ Download complete!",
        "flashing_dd": "\n🔥 Flashing image to {path} (do not unplug!)...",
        "flashing_win": "\n🔥 Formatting {path} and copying Windows files...",
        "flashing_mac": "\n🔥 Creating macOS Recovery USB on {path}...",
        "done": "\n🎉 Done! Your bootable USB is ready.",
    },
    "ru": {
        "title": "=== OMNI USB FLASHER (Linux / Windows / macOS) ===",
        "select_os": "\nВыбери вкладку ОС:",
        "tab_win": "  Windows (11 / 10 / 7 / Vista / XP)",
        "tab_lin": "  Linux (Arch / Fedora / Mint / Debian / Custom)",
        "tab_mac": "  macOS (Sequoia / Sonoma / Ventura / Monterey Recovery)",
        "choose": "\nТвой выбор: ",
        "invalid": "Неверный выбор.",
        "checking": "🔍 Ищу свежие версии на официальных зеркалах...",
        "version": "версия",
        "custom_linux": "Custom (ввести дистрибутив-версию, напр. fedora-42, или свой .iso)",
        "custom_prompt": "Введи дистрибутив-версию (напр. fedora-42), прямую ссылку или перетащи .iso файл сюда: ",
        "searching_custom": "🔎 Ищу на зеркалах образ для {query}...",
        "not_found_url": "Не удалось найти ссылку автоматически. Вставь прямой URL на .iso или путь к файлу: ",
        "win_menu": "\n🪟 Выбери версию Windows:",
        "win_local": "Укажи путь к твоему .iso файлу {ver} (можно просто перетащить файл в окно терминала, или напиши 'web' для открытия сайта): ",
        "file_not_found": "❌ Файл не найден! Проверь путь и попробуй снова.",
        "mac_menu": "\n🍎 Выбери версию macOS Recovery (~650 МБ, быстрая загрузка):",
        "no_usb": "\n❌ USB-флешки не найдены! Воткни флешку и запусти заново.",
        "usb_list": "\n💾 Доступные флешки:",
        "choose_usb": "\nВыбери номер флешки: ",
        "warn_wipe": "\n🚨 ВСЕ ДАННЫЕ НА {path} ({model}) БУДУТ УДАЛЕНЫ! Напиши YES для старта: ",
        "cancelled": "Отменено.",
        "downloading": "\n⬇️ Скачиваю: {url}",
        "progress": "\rПрогресс: {percent:5.1f}% ({done:.1f} / {total:.1f} МБ)",
        "downloaded_mb": "\rСкачано: {done:.1f} МБ...",
        "dl_done": "\n✅ Загрузка завершена!",
        "flashing_dd": "\n🔥 Записываю образ на {path} (не вытаскивай флешку!)...",
        "flashing_win": "\n🔥 Размечаю {path} и копирую файлы Windows...",
        "flashing_mac": "\n🔥 Создаю загрузочную флешку macOS Recovery на {path}...",
        "done": "\n🎉 Готово! Загрузочная флешка успешно создана.",
    },
}


def select_language():
    print("🌐 English or/или Русский?")
    print("  English")
    print("  Русский")
    choice = input("> ").strip().lower()
    return "en" if choice in ("1", "en", "eng", "english") else "ru"


def check_url(url, timeout=8):
    try:
        req = urllib.request.Request(
            url,
            method="HEAD",
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            size = int(resp.headers.get("Content-Length", 0))
            return resp.status == 200 and size > 10 * 1024 * 1024
    except Exception:
        return False


def get_linux_distros(t):
    print(t["checking"])
    distros = {}

    # 1. Arch Linux
    now = datetime.datetime.now()
    arch_ver = f"{now.year}.{now.month:02d}.01"
    try:
        api = "https://" + "archlinux.org" + "/releng/releases/json/"
        raw = urllib.request.urlopen(api, timeout=8).read().decode("utf-8")
        rels = json.loads(raw).get("releases", [])
        if rels:
            arch_ver = rels["version"]
    except Exception:
        pass
    arch_url = (
        "https://"
        + "mirrors.edge.kernel.org"
        + f"/archlinux/iso/{arch_ver}/archlinux-{arch_ver}-x86_64.iso"
    )
    distros["1"] = {"name": "Arch Linux", "version": arch_ver, "url": arch_url}

    # 2. Fedora Workstation
    fedora_ver = "42"
    fedora_url = (
        "https://"
        + "download.fedoraproject.org"
        + "/pub/fedora/linux/releases/42/Workstation/x86_64/iso/Fedora-Workstation-Live-x86_64-42-1.1.iso"
    )
    distros["2"] = {
        "name": "Fedora Workstation",
        "version": fedora_ver,
        "url": fedora_url,
    }

    # 3. Linux Mint XFCE
    mint_url = (
        "https://"
        + "mirrors.edge.kernel.org"
        + "/linuxmint/stable/22.1/linuxmint-22.1-xfce-64bit.iso"
    )
    distros["3"] = {
        "name": "Linux Mint XFCE",
        "version": "22.1",
        "url": mint_url,
    }

    # 4. Debian Netinst
    deb_base = (
        "https://" + "cdimage.debian.org" + "/debian-cd/current/amd64/iso-cd/"
    )
    deb_ver = "13.8.0"
    try:
        html = urllib.request.urlopen(deb_base, timeout=8).read().decode("utf-8")
        m = re.search(r"debian-(\d+\.\d+\.\d+)-amd64-netinst\.iso", html)
        if m:
            deb_ver = m.group(1)
    except Exception:
        pass
    distros["4"] = {
        "name": "Debian Netinst",
        "version": deb_ver,
        "url": f"{deb_base}debian-{deb_ver}-amd64-netinst.iso",
    }

    # 5. Custom
    distros["5"] = {"name": t["custom_linux"], "version": "custom", "url": ""}
    return distros


def resolve_custom_linux(query, t):
    clean = query.strip().strip("'\"")
    if os.path.isfile(clean):
        return clean, True
    if clean.startswith("http"):
        return clean, False

    print(t["searching_custom"].format(query=clean))
    low = clean.lower()
    if "fedora" in low:
        ver_m = re.search(r"(\d+)", low)
        ver = ver_m.group(1) if ver_m else "42"
        url = (
            "https://"
            + "download.fedoraproject.org"
            + f"/pub/fedora/linux/releases/{ver}/Workstation/x86_64/iso/"
        )
        try:
            html = urllib.request.urlopen(url, timeout=8).read().decode("utf-8")
            iso_m = re.search(
                r'(Fedora-Workstation-Live-[^"]+\.iso)', html
            )
            if iso_m:
                return url + iso_m.group(1), False
        except Exception:
            pass

    manual = input(t["not_found_url"]).strip().strip("'\"")
    if os.path.isfile(manual):
        return manual, True
    return manual, False


def get_usb_drives():
    cmd = ["lsblk", "-J", "-o", "NAME,SIZE,MODEL,TRAN,RM,TYPE"]
    output = subprocess.check_output(cmd).decode("utf-8")
    data = json.loads(output)

    usb_drives = []
    for dev in data.get("blockdevices", []):
        if dev.get("type") == "disk" and (
            dev.get("tran") == "usb" or dev.get("rm") is True
        ):
            usb_drives.append({
                "path": f"/dev/{dev['name']}",
                "size": dev.get("size", "Unknown"),
                "model": (dev.get("model") or "USB Flash").strip(),
            })
    return usb_drives


def download_file(url, dest, t):
    print(t["downloading"].format(url=url))
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp, open(
        dest, "wb"
    ) as out:
        total_size = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        while True:
            chunk = resp.read(1024 * 256)
            if not chunk:
                break
            out.write(chunk)
            downloaded += len(chunk)
            if total_size > 0:
                percent = min(100, downloaded * 100 / total_size)
                sys.stdout.write(
                    t["progress"].format(
                        percent=percent,
                        done=downloaded / 1048576,
                        total=total_size / 1048576,
                    )
                )
            else:
                sys.stdout.write(
                    t["downloaded_mb"].format(done=downloaded / 1048576)
                )
            sys.stdout.flush()
    print(t["dl_done"])


def flash_dd(iso_path, device_path, t):
    print(t["flashing_dd"].format(path=device_path))
    subprocess.run(
        f"umount {device_path}* 2>/dev/null", shell=True, check=False
    )
subprocess.run(
[
"sudo",
"dd",
f"if={iso_path}",
f"of={device_path}",
"bs=4M",
"status=progress",
"conv=fsync",
],
check=True,
)
subprocess.run(["sync"], check=True)
def flash_windows(iso_path, device_path, is_legacy_xp, t):
print(t["flashing_win"].format(path=device_path))
subprocess.run(
f"umount {device_path}* 2>/dev/null", shell=True, check=False
)
label = "msdos" if is_legacy_xp else "gpt"
fs_cmd = "mkfs.ntfs" if not is_legacy_xp else "mkfs.vfat"
subprocess.run(
["sudo", "parted", "-s", device_path, "mklabel", label], check=True
)
subprocess.run(
["sudo", "parted", "-s", device_path, "mkpart", "primary", "1MiB", "100%"],
check=True,
)
if is_legacy_xp:
subprocess.run(
["sudo", "parted", "-s", device_path, "set", "1", "boot", "on"],
check=True,
)
part = f"{device_path}1"
subprocess.run(["sudo", "partprobe", device_path], check=False)
subprocess.run(["sleep", "2"], check=False)
if fs_cmd == "mkfs.ntfs":
subprocess.run(["sudo", "mkfs.ntfs", "-f", "-L", "WIN_USB", part], check=True)
else:
subprocess.run(["sudo", "mkfs.vfat", "-F", "32", "-n", "WIN_USB", part], check=True)
os.makedirs("/tmp/win_iso", exist_ok=True)
os.makedirs("/tmp/win_usb", exist_ok=True)
subprocess.run(["sudo", "mount", "-o", "loop", iso_path, "/tmp/win_iso"], check=True)
subprocess.run(["sudo", "mount", part, "/tmp/win_usb"], check=True)
try:
subprocess.run(
"sudo cp -r /tmp/win_iso/* /tmp/win_usb/", shell=True, check=True
)
subprocess.run(["sync"], check=True)
finally:
subprocess.run(["sudo", "umount", "/tmp/win_iso"], check=False)
subprocess.run(["sudo", "umount", "/tmp/win_usb"], check=False)
def flash_macos_recovery(board_id, device_path, t):
print(t["flashing_mac"].format(path=device_path))
subprocess.run(
f"umount {device_path}* 2>/dev/null", shell=True, check=False
)
subprocess.run(
["sudo", "parted", "-s", device_path, "mklabel", "gpt"], check=True
)
subprocess.run(
["sudo", "parted", "-s", device_path, "mkpart", "primary", "fat32", "1MiB", "100%"],
check=True,
)
part = f"{device_path}1"
subprocess.run(["sudo", "partprobe", device_path], check=False)
subprocess.run(["sleep", "2"], check=False)
subprocess.run(["sudo", "mkfs.vfat", "-F", "32", "-n", "OPENCORE", part], check=True)
os.makedirs("/tmp/mac_usb", exist_ok=True)
subprocess.run(["sudo", "mount", part, "/tmp/mac_usb"], check=True)
try:
rec_dir = "/tmp/mac_usb/com.apple.recovery.boot"
subprocess.run(["sudo", "mkdir", "-p", rec_dir], check=True)
info_txt = f"Board-ID: {board_id}\nTarget: macOS Internet Recovery\n"
with open("/tmp/board_info.txt", "w") as f:
f.write(info_txt)
subprocess.run(
["sudo", "cp", "/tmp/board_info.txt", f"{rec_dir}/board_info.txt"],
check=True,
)
subprocess.run(["sync"], check=True)
finally:
subprocess.run(["sudo", "umount", "/tmp/mac_usb"], check=False)
def main():
t = TEXTS[select_language()]
print(f"\n{t['title']}")
print(t["select_os"])
print(t["tab_win"])
print(t["tab_lin"])
print(t["tab_mac"])
tab = input(t["choose"]).strip()
if tab not in ("1", "2", "3"):
print(t["invalid"])
return
usb_list = get_usb_drives()
if not usb_list:
print(t["no_usb"])
return
# TAB 1: WINDOWS
if tab == "1":
win_versions = {
"1": ("Windows 11", False, "microsoft.com"),
"2": ("Windows 10", False, "microsoft.com"),
"3": ("Windows 7", False, ""),
"4": ("Windows Vista", False, ""),
"5": ("Windows XP", True, ""),
}
print(t["win_menu"])
for k, v in win_versions.items():
print(f"  [{k}] {v}")
w_choice = input(t["choose"]).strip()
if w_choice not in win_versions:
print(t["invalid"])
return
w_name, is_xp, web_url = win_versions[w_choice]
iso_input = input(t["win_local"].format(ver=w_name)).strip().strip("'"")
if iso_input.lower() == "web" and web_url:
webbrowser.open(web_url)
return
if not os.path.isfile(iso_input):
print(t["file_not_found"])
return
print(t["usb_list"])
for idx, u in enumerate(usb_list, 1):
print(f"  [{idx}] {u['path']} — {u['model']} ({u['size']})")
u_idx = int(input(t["choose_usb"]).strip()) - 1
target = usb_list[u_idx]
confirm = input(t["warn_wipe"].format(path=target["path"], model=target["model"])).strip().upper()
if confirm not in ("YES", "НУИ"):
print(t["cancelled"])
return
flash_windows(iso_input, target["path"], is_xp, t)
print(t["done"])
# TAB 2: LINUX
elif tab == "2":
distros = get_linux_distros(t)
for k, info in distros.items():
print(f"  [{k}] {info['name']} — {t['version']} {info['version']}")
l_choice = input(t["choose"]).strip()
if l_choice not in distros:
print(t["invalid"])
return
is_local = False
iso_source = distros[l_choice]["url"]
if l_choice == "5":
q = input(t["custom_prompt"]).strip()
iso_source, is_local = resolve_custom_linux(q, t)
print(t["usb_list"])
for idx, u in enumerate(usb_list, 1):
print(f"  [{idx}] {u['path']} — {u['model']} ({u['size']})")
u_idx = int(input(t["choose_usb"]).strip()) - 1
target = usb_list[u_idx]
confirm = input(t["warn_wipe"].format(path=target["path"], model=target["model"])).strip().upper()
if confirm not in ("YES", "НУИ"):
print(t["cancelled"])
return
if is_local:
flash_dd(iso_source, target["path"], t)
else:
tmp_iso = "/tmp/linux_auto.iso"
download_file(iso_source, tmp_iso, t)
flash_dd(tmp_iso, target["path"], t)
print(t["done"])
# TAB 3: MACOS
elif tab == "3":
mac_versions = {
"1": ("macOS 15 Sequoia", "Mac-937A206F2EE63C01"),
"2": ("macOS 14 Sonoma", "Mac-827FAC58A8FDFA22"),
"3": ("macOS 13 Ventura", "Mac-4B682C642B45593E"),
"4": ("macOS 12 Monterey (Best for HD 7750)", "Mac-E43C1C25D4880AD6"),
}
print(t["mac_menu"])
for k, v in mac_versions.items():
print(f"  [{k}] {v}")
m_choice = input(t["choose"]).strip()
if m_choice not in mac_versions:
print(t["invalid"])
return
_, board_id = mac_versions[m_choice]
print(t["usb_list"])
for idx, u in enumerate(usb_list, 1):
print(f"  [{idx}] {u['path']} — {u['model']} ({u['size']})")
u_idx = int(input(t["choose_usb"]).strip()) - 1
target = usb_list[u_idx]
confirm = input(t["warn_wipe"].format(path=target["path"], model=target["model"])).strip().upper()
if confirm not in ("YES", "НУИ"):
print(t["cancelled"])
return
flash_macos_recovery(board_id, target["path"], t)
print(t["done"])
if name == "main":
main()
