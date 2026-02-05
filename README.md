# MLCleaner (MyLightCleaner) v0.3
### The Ultra-Lightweight System Optimizer for Linux

[![Website](https://img.shields.io/badge/Website-mylightcleaner.vercel.app-blue?style=for-the-badge)](https://mylightcleaner.vercel.app/)
[![Platform](https://img.shields.io/badge/Platform-Linux-orange?style=for-the-badge)](https://github.com/kaneki654/MLC)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://www.python.org/)

**MLCleaner** is a professional, **high-performance system cleaner** and **desktop optimizer** designed specifically for **Linux distributions** (Ubuntu, Debian, Fedora, Arch, etc.). It helps you reclaim gigabytes of disk space, monitor system health, and secure your privacy with a modern, intuitive interface.

---

## 💻 GUI and CLI Support
MLCleaner now comes in two flavors:
- **Desktop (GUI):** A beautiful, professional interface built with CustomTkinter.
- **Terminal (CLI):** A powerful, high-speed terminal interface built with `rich` for power users and server environments.

👉 **[Explore MLCleaner-CLI Source](./CLI)**

---

## 🔥 Why MLCleaner?
If you are looking for a **Stacer alternative** or a more modern **BleachBit alternative**, MLCleaner provides a faster, developer-centric approach to system maintenance.

- **Lightweight:** Minimal CPU and RAM footprint.
- **Developer First:** Built-in support for cleaning **Docker**, **NPM**, **Python (Pip)**, and **Git** artifacts.
- **Privacy Focused:** Securely prunes browser history and sensitive caches.
- **Intelligent:** Real-time **SSD Health monitoring** and **security permission analysis**.

---

## 🚀 Key Features

### 🧹 Advanced Junk Removal
*   **System Maintenance:** Clear **APT cache**, thumbnail databases, and `/tmp` directories.
*   **Browser Privacy:** Support for **Chrome, Chromium, Firefox, and Brave**—remove trackers and redundant caches.
*   **Modern App Support:** Deep clean **Flatpak runtimes**, **Snap packages**, Discord, and Spotify data.
*   **Dev Center:** One-click cleanup for **Pip, NPM, Yarn, Cargo registry, and Gradle** project bloat.

### 🏥 System Health & Security (New in v0.3)
*   **System Optimizer:** Deep RAM flushing and Swap memory defragmentation.
*   **Kernel Tuning:** Optimized profiles for Gaming and Battery life.
*   **Safe Cleaning:** Integrated **Trash support** and secure DOD-level shredding.
*   **Seamless Auth:** Internal password dialogs for a professional, no-terminal experience.

### 🔍 Deep Analysis Tools
*   **Duplicate Finder:** Identify identical files using **MD5 cryptographic hashing**.
*   **Large Cluster Explorer:** Visual block-based analysis of large file storage.
*   **Broken Symlink Detector:** Locate and repair invalid system shortcuts.
*   **Ghost Process Monitor:** Find deleted files still consuming space via open file descriptors.

---

## 📥 Installation

### Desktop Version (.deb)
Download the latest **.deb** package for Debian/Ubuntu-based systems directly from our official page:

👉 **[Download MLCleaner v0.3](https://mylightcleaner.vercel.app/)**

```bash
# To install the downloaded .deb package
sudo dpkg -i MLCleaner_v0.3_all.deb
sudo apt install -f
```

### CLI Version (Manual)
```bash
git clone https://github.com/kaneki654/MLC.git
cd MLC/CLI
pip install -r requirements.txt
python3 main.py
```

---

## 📦 Releases

| Version | Type | Release Date | Status |
|---------|------|--------------|--------|
| **v0.3.0.1** | CLI | 2026-02-05 | [Latest] |
| **v0.3.0** | GUI | 2026-02-05 | [Stable] |
| **v0.2.0** | GUI | 2026-02-05 | Legacy |
| **v0.1.0** | GUI | 2026-02-04 | Initial |

---

## 🛠️ Built With
- **Python 3**: Core logic and system integration.
- **CustomTkinter**: Modern, GPU-accelerated GUI.
- **Rich**: Beautiful CLI formatting and progress tracking.
- **Psutil**: High-precision resource monitoring.
- **Smartmontools**: Advanced hardware health diagnostics.

---

## 🤝 Contributing & Feedback
Contributions are welcome! If you have ideas for **Linux optimization** or feature requests, feel free to:
1. Open a **Pull Request**.
2. Submit an **Issue** on [GitHub](https://github.com/kaneki654/MLC/issues).

---

## 📜 Version History

### [v0.3.0.1] - 2026-02-05 (CLI)
- **Terminal Optimization:** Modular architecture for high-speed terminal interaction.
- **Rich TUI:** Tables, panels, and live updates in the terminal.
- **Process Sentinel (Live):** Real-time process monitoring with a 3-second refresh cycle.
- **Internal Auth:** Integrated `getpass` for secure `sudo` operations.

### [v0.3.0] - 2026-02-05 (GUI)
**Intelligence Update: Power & Control**
- **System Optimizer:** Real-time RAM/Swap flushing and Kernel PageCache purging.
- **Kernel Tuner:** Integrated profiles for Gaming, Balanced, and Power Saving.
- **Global SCAN:** Expanded "Large Files" to root-level global search.
- **Native Trash:** Added "Move to Trash" support.

### [v0.2.0] - 2026-02-05
**Security Update: Health & Monitoring**
- **SMART Monitor:** Physical drive longevity tracking.
- **Permission Analyzer:** Harden world-writable files in Home directory.

---
---

**Keywords:** Linux Cleaner, System Optimizer, CLI System Tools, Ubuntu Optimizer, Python Desktop App, Terminal Junk Remover, BleachBit Alternative, Stacer Alternative, Docker Prune GUI, Flatpak Cleanup, Linux Security Tool.

<p align="center">
  Developed By <strong>G0Ju.VBS</strong>
</p>
