#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run Garmin Connect IQ app on selected device(s) from manifest_devices.txt with a simple GUI.

- Reads device IDs (one per line) from manifest_devices.txt (same folder as this script by default).
- Lets you pick a device from a dropdown.
- Starts the Simulator if not already running.
- Loads your .prg onto the selected device via monkeydo.bat.
- Remembers your paths in run_garmin.settings.json (next to this script).

Tested on Windows. Requires Python 3.9+.
"""

import json
import os
import sys
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_TITLE = "Garmin Loader (manifest_devices.txt)"
SETTINGS_FILE = "run_garmin.settings.json"
DEFAULT_DEVICE_LIST = "manifest_devices.txt"

# Reasonable defaults (edit to your environment, or browse in the UI)
DEFAULTS = {
    "sdk_bin": r"C:\Users\simonedwards\AppData\Roaming\Garmin\ConnectIQ\Sdks\connectiq-sdk-win-8.2.3-2025-08-11-cac5b3b21\bin",
    "app_prg": r"D:\OneDrive\Garmin\Source\CleanAnalogPremium\bin\CleanAnalogPremium.prg",
    "device_list": DEFAULT_DEVICE_LIST
}

def script_dir():
    return os.path.dirname(os.path.abspath(__file__))

def load_settings():
    path = os.path.join(script_dir(), SETTINGS_FILE)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULTS, **data}
        except Exception:
            return DEFAULTS.copy()
    return DEFAULTS.copy()

def save_settings(settings: dict):
    path = os.path.join(script_dir(), SETTINGS_FILE)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Warning: failed to save settings: {e}")

def read_device_list(filepath: str):
    devices = []
    if not filepath:
        return devices
    if not os.path.isabs(filepath):
        filepath = os.path.join(script_dir(), filepath)
    if not os.path.exists(filepath):
        return devices
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith(";"):
                continue
            # Accept lines like: fr970  or  device=fr970  or "fr970"
            if "=" in line:
                line = line.split("=", 1)[1].strip()
            line = line.strip("\"' ")
            if line:
                devices.append(line)
    return devices

def is_simulator_running():
    # Windows-only check using tasklist
    try:
        out = subprocess.check_output(["tasklist", "/fi", "imagename eq simulator.exe"], creationflags=subprocess.CREATE_NO_WINDOW)
        return b"simulator.exe" in out.lower()
    except Exception:
        return False

def start_simulator(sdk_bin: str, log_fn):
    sim_path = os.path.join(sdk_bin, "simulator.exe")
    if not os.path.exists(sim_path):
        raise FileNotFoundError(f"Simulator not found: {sim_path}")
    if is_simulator_running():
        log_fn("Simulator already running.\n")
        return
    log_fn(f"Starting Simulator: {sim_path}\n")
    # Start without waiting
    subprocess.Popen([sim_path], cwd=sdk_bin, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Give it a moment to boot
    for _ in range(30):
        if is_simulator_running():
            log_fn("Simulator is up.\n")
            return
        time.sleep(0.2)
    log_fn("Warning: Simulator did not appear to start within 6 seconds. Continuing anyway...\n")

def run_monkeydo(sdk_bin: str, app_prg: str, device: str, log_fn):
    mdo = os.path.join(sdk_bin, "monkeydo.bat")
    if not os.path.exists(mdo):
        raise FileNotFoundError(f"monkeydo.bat not found: {mdo}")
    if not os.path.exists(app_prg):
        raise FileNotFoundError(f".prg not found: {app_prg}")
    cmd = ["cmd", "/c", mdo, app_prg, device]
    log_fn(f"Running: {' '.join(cmd)}\n")
    try:
        # Stream output to UI
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        for line in iter(proc.stdout.readline, ""):
            if not line:
                break
            log_fn(line)
        proc.wait()
        rc = proc.returncode
        log_fn(f"\nmonkeydo exit code: {rc}\n")
        return rc
    except FileNotFoundError:
        raise
    except Exception as e:
        log_fn(f"Error running monkeydo: {e}\n")
        return -1

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("760x520")
        self.minsize(720, 480)

        self.settings = load_settings()
        self.devices = read_device_list(self.settings.get("device_list"))
        self.running = False

        self.create_widgets()
        self.refresh_devices()

    def create_widgets(self):
        pad = {"padx": 8, "pady": 6}

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True)

        # SDK bin
        ttk.Label(frm, text="SDK bin:").grid(row=0, column=0, sticky="w", **pad)
        self.sdk_var = tk.StringVar(value=self.settings.get("sdk_bin", ""))
        ttk.Entry(frm, textvariable=self.sdk_var, width=80).grid(row=0, column=1, sticky="we", **pad)
        ttk.Button(frm, text="Browse…", command=self.browse_sdk).grid(row=0, column=2, **pad)

        # .prg
        ttk.Label(frm, text=".prg file:").grid(row=1, column=0, sticky="w", **pad)
        self.prg_var = tk.StringVar(value=self.settings.get("app_prg", ""))
        ttk.Entry(frm, textvariable=self.prg_var, width=80).grid(row=1, column=1, sticky="we", **pad)
        ttk.Button(frm, text="Browse…", command=self.browse_prg).grid(row=1, column=2, **pad)

        # manifest_devices
        ttk.Label(frm, text="Device list:").grid(row=2, column=0, sticky="w", **pad)
        self.devlist_var = tk.StringVar(value=self.settings.get("device_list", DEFAULT_DEVICE_LIST))
        ttk.Entry(frm, textvariable=self.devlist_var, width=80).grid(row=2, column=1, sticky="we", **pad)
        ttk.Button(frm, text="Browse…", command=self.browse_devlist).grid(row=2, column=2, **pad)

        frm.grid_columnconfigure(1, weight=1)

        # Device selector
        ttk.Label(frm, text="Select device:").grid(row=3, column=0, sticky="w", **pad)
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(frm, textvariable=self.device_var, state="readonly", width=40, values=self.devices)
        self.device_combo.grid(row=3, column=1, sticky="w", **pad)

        # Buttons
        btnfrm = ttk.Frame(frm)
        btnfrm.grid(row=3, column=2, sticky="e", **pad)
        ttk.Button(btnfrm, text="Refresh", command=self.refresh_devices).pack(side="left", padx=4)
        self.run_btn = ttk.Button(btnfrm, text="Run", command=self.on_run)
        self.run_btn.pack(side="left", padx=4)

        # Output
        ttk.Label(frm, text="Output:").grid(row=4, column=0, sticky="nw", **pad)
        self.out = tk.Text(frm, height=18, wrap="word")
        self.out.grid(row=4, column=1, columnspan=2, sticky="nsew", **pad)
        frm.grid_rowconfigure(4, weight=1)

        # Status bar
        self.status = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status, anchor="w").pack(fill="x", padx=6, pady=4)

        # Close handler
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def log(self, msg: str):
        self.out.insert("end", msg)
        self.out.see("end")

    def set_busy(self, busy: bool):
        self.running = busy
        state = "disabled" if busy else "normal"
        self.run_btn.config(state=state)
        self.device_combo.config(state="disabled" if busy else "readonly")
        self.status.set("Working…" if busy else "Ready")
        self.update_idletasks()

    def browse_sdk(self):
        path = filedialog.askdirectory(title="Select Connect IQ SDK bin folder")
        if path:
            self.sdk_var.set(path)

    def browse_prg(self):
        path = filedialog.askopenfilename(title="Select .prg file", filetypes=[("Garmin PRG", "*.prg"), ("All files", "*.*")])
        if path:
            self.prg_var.set(path)

    def browse_devlist(self):
        path = filedialog.askopenfilename(title="Select manifest_devices.txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            self.devlist_var.set(path)
            self.refresh_devices()

    def refresh_devices(self):
        devices = read_device_list(self.devlist_var.get())
        self.devices = devices
        self.device_combo["values"] = devices
        if devices:
            self.device_combo.current(0)
        else:
            self.device_combo.set("")
        self.log(f"Loaded {len(devices)} device(s) from {self.devlist_var.get()}\n")

    def on_run(self):
        device = self.device_var.get().strip()
        if not device:
            messagebox.showerror(APP_TITLE, "Please select a device.")
            return

        sdk_bin = self.sdk_var.get().strip().strip('"')
        app_prg = self.prg_var.get().strip().strip('"')
        devlist = self.devlist_var.get().strip()

        if not os.path.isdir(sdk_bin):
            messagebox.showerror(APP_TITLE, f"SDK bin not found:\n{sdk_bin}")
            return
        if not os.path.exists(app_prg):
            messagebox.showerror(APP_TITLE, f".prg file not found:\n{app_prg}")
            return

        # Persist settings
        self.settings.update({"sdk_bin": sdk_bin, "app_prg": app_prg, "device_list": devlist})
        save_settings(self.settings)

        def worker():
            try:
                self.set_busy(True)
                self.log(f"\n=== Device: {device} ===\n")
                start_simulator(sdk_bin, self.log)
                # Small delay to let simulator settle
                time.sleep(0.5)
                rc = run_monkeydo(sdk_bin, app_prg, device, self.log)
                if rc == 0:
                    self.log("Done.\n")
                else:
                    self.log("Finished with errors.\n")
            except FileNotFoundError as e:
                messagebox.showerror(APP_TITLE, str(e))
            except Exception as e:
                messagebox.showerror(APP_TITLE, f"Unexpected error: {e}")
            finally:
                self.set_busy(False)

        threading.Thread(target=worker, daemon=True).start()

    def on_close(self):
        # Save on exit
        self.settings.update({
            "sdk_bin": self.sdk_var.get().strip(),
            "app_prg": self.prg_var.get().strip(),
            "device_list": self.devlist_var.get().strip(),
        })
        save_settings(self.settings)
        self.destroy()

def main():
    # Make console DPI aware (cosmetic)
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Per-monitor DPI aware
        except Exception:
            pass

    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
