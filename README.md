# ⚡ Omni USB Flasher

**One single `.py` file to turn any USB drive into a bootable installer for Linux, Windows, or macOS.**  
**Один `.py` файл, который превратит твою флешку в загрузочник для Linux, Windows или macOS.**

🌐 **Bilingual UI (English / Русский)** • 📦 **Zero external Python dependencies** • 🛡️ **Anti-brick disk protection**

---

## 🚀 Features / Возможности

### 🐧 Linux Tab / Вкладка Linux
* **Auto-discovery:** Automatically fetches the latest releases directly from official mirrors (**Arch Linux, Fedora Workstation, Linux Mint XFCE, Debian**).
* **Custom Mode:** Enter any distro & version (e.g. `fedora-42`), paste a direct `.iso` link, or drag & drop a local `.iso` file to skip long downloads.
* **Автопоиск версий:** Сам находит свежие релизы на официальных зеркалах.
* **Режим Custom:** Можно ввести дистрибутив и версию, вставить прямую ссылку или просто перетащить локальный `.iso` файл в терминал.

### 🪟 Windows Tab (XP / Vista / 7 / 10 / 11)
* Smart partitioning & formatting instead of raw `dd` (so Windows installers actually boot on real hardware):
  * **GPT + NTFS** for modern Windows (Vista / 7 / 10 / 11).
  * **MBR + FAT32 (boot flag)** for legacy Windows XP.
* Умная разметка и распаковка файлов (в отличие от обычного `dd`, флешка с Windows реально загружается на ПК).

### 🍎 macOS Tab (Internet Recovery)
* Fast creation of **macOS Recovery** bootable USB drives (**Monterey, Ventura, Sonoma, Sequoia**) using official Apple Board-IDs (~650 MB instead of 15 GB).
* Быстрое создание загрузочной флешки **macOS Recovery** (~650 МБ вместо 15 ГБ).

### 🛡️ Safety First / Защита от ошибок
* Scans only removable USB drives (`lsblk`), protecting your internal system SSD/HDD from accidental wipes.
* Verifies downloaded file size to prevent flashing broken HTML redirect pages.
* Показывает только съёмные USB-флешки и защищает системные диски от случайного форматирования.

---

## 🛠️ Requirements / Требования

* **OS:** Linux (tested on Bazzite / Fedora / Arch / Debian)
* **Python:** 3.8+ (uses only built-in standard library!)
* **System utilities:** `lsblk`, `dd`, `parted`, `mkfs.vfat`, `mkfs.ntfs` (pre-installed on most distros)

---

## ⚡ Quick Start / Быстрый запуск

```bash
git clone https://github.com
cd disto-usb-flasher
python3 disto_flasher.py
```

---

## 📄 License / Лицензия

Distributed under the **MIT License**. See `LICENSE` for more information.
