# Community Validation & Testing Guide

To ensure MLCleaner remains stable and trustworthy, we encourage community members to participate in validation.

## 🧪 How to Verify Features
You can verify the implementation of any feature by checking the [Feature Matrix](./FEATURES.md).

### 1. Manual Testing
We recommend testing in a virtual machine (Ubuntu 22.04 or 24.04).
- **Scan Engine:** Run a scan and verify the discovered file sizes against your actual `/tmp` or `.cache` directories.
- **Root SCAN:** Use the Toolbox SCAN and verify it finds files in `/root` (requires sudo).
- **RAM Boost:** Check `free -h` before and after clicking the RAM Boost button.

### 2. Technical Validation
If you are a developer, you can inspect the code:
- **Zero-Lag Logic:** Inspect `PyCleaner/ui/components.py` for the implementation of `InfiniteScrollFrame` (Row Pooling).
- **Authentication:** Inspect `PyCleaner/core/auth.py` to see how passwords are handled (We use piped inputs, we never store passwords).

## 🐛 Reporting Bugs
When reporting a bug on the [Issues](https://github.com/kaneki654/MLC/issues) page, please include:
1. Your Linux distribution and version.
2. The version of MLCleaner (found in the Title Bar).
3. Steps to reproduce the issue.
4. (Optional) Screenshot or terminal output.

## 🤝 Community Validation Status
We are looking for maintainers! If you have validated a specific feature on a unique hardware configuration (e.g., AMD A4, Raspberry Pi), please let us know in the issues.

---
*Join us in building the most transparent system optimizer for Linux.*
