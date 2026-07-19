import tkinter as tk
from tkinter import ttk
import numpy as np

class DistillationHMI:
    def __init__(self, root):
        self.root = root
        self.root.title("MIMO Distillation Control Room - Layer 3 HMI")
        self.root.geometry("700x580")
        self.root.configure(bg="#1e1e1e")

        # Custom Styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Arial", 11))
        style.configure("TScale", background="#1e1e1e")

        # Title Header
        title = tk.Label(root, text="DISTILLATION COLUMN TELEMETRY INTERFACE", 
                         bg="#2d2d2d", fg="#00ff00", font=("Arial", 14, "bold"), pady=10)
        title.pack(fill=tk.X)

        # Main Layout Frame
        main_frame = tk.Frame(root, bg="#1e1e1e", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- TELEMETRY CONTROL PANEL (OT Emulation Sliders) ---
        slider_frame = tk.LabelFrame(main_frame, text=" Live Field Emulation Sliders ", 
                                     bg="#1e1e1e", fg="#00ff00", font=("Arial", 10, "bold"), padx=15, pady=15)
        slider_frame.grid(row=0, column=0, sticky="nsew", padx=10)

        # 1. Temperature Control Group
        ttk.Label(slider_frame, text="Column Temperature (°C):").pack(anchor=tk.W, pady=(5, 2))
        self.temp_var = tk.DoubleVar(value=80.0)
        self.temp_scale = ttk.Scale(slider_frame, from_=50.0, to_=150.0, variable=self.temp_var, 
                                    orient=tk.HORIZONTAL, command=self.update_indicators)
        self.temp_scale.pack(fill=tk.X)
        
        self.temp_lbl = ttk.Label(slider_frame, text="Current: 80.0 °C")
        self.temp_lbl.pack(anchor=tk.E, pady=(2, 15))

        # 2. Controller Demand Output Group
        ttk.Label(slider_frame, text="Controller Demand Output (%):").pack(anchor=tk.W, pady=(5, 2))
        self.pid_var = tk.DoubleVar(value=50.0)
        self.pid_scale = ttk.Scale(slider_frame, from_=0.0, to_=100.0, variable=self.pid_var, 
                                   orient=tk.HORIZONTAL, command=self.update_indicators)
        self.pid_scale.pack(fill=tk.X)
        
        self.pid_lbl = ttk.Label(slider_frame, text="Demand: 50.0 %")
        self.pid_lbl.pack(anchor=tk.E, pady=(2, 15))

        # 3. Physical Valve Feedback Group
        ttk.Label(slider_frame, text="Physical Valve Feedback (%):").pack(anchor=tk.W, pady=(5, 2))
        self.valve_var = tk.DoubleVar(value=50.0)
        self.valve_scale = ttk.Scale(slider_frame, from_=0.0, to_=100.0, variable=self.valve_var, 
                                     orient=tk.HORIZONTAL, command=self.update_indicators)
        self.valve_scale.pack(fill=tk.X)
        
        self.valve_lbl = ttk.Label(slider_frame, text="Feedback: 50.0 %")
        self.valve_lbl.pack(anchor=tk.E, pady=(2, 10))
        
        # Separator line before delta metric
        ttk.Label(slider_frame, text="----------------------------------------", foreground="#444444").pack(anchor=tk.E)
        
        # Delta Deviation Readout
        self.stiction_lbl = ttk.Label(slider_frame, text="Valve Delta: 0.0 %", font=("Arial", 11, "bold"))
        self.stiction_lbl.pack(anchor=tk.E, pady=(5, 0))

        # --- INDUSTRIAL MONITORING INDICATORS ---
        status_frame = tk.LabelFrame(main_frame, text=" System Status & Safety Alarms ", 
                                     bg="#1e1e1e", fg="#00ff00", font=("Arial", 10, "bold"), padx=15, pady=15)
        status_frame.grid(row=0, column=1, sticky="nsew", padx=10)

        # Interlock LED Display
        self.sis_led = tk.Label(status_frame, text="SIS INTERLOCK: NORMAL", 
                                bg="#008000", fg="#ffffff", font=("Arial", 11, "bold"), width=25, height=2)
        self.sis_led.pack(pady=15)

        # AI Anomaly Warning Box
        self.ai_box = tk.Label(status_frame, text="AI PREDICTIVE MAINTENANCE\nSignatures Nominal\nNo Anomalies Found", 
                               bg="#2d2d2d", fg="#ffffff", font=("Arial", 10), width=25, height=5, relief=tk.SUNKEN)
        self.ai_box.pack(pady=15)

        # Initial calculation update
        self.update_indicators()

    def update_indicators(self, *args):
        # Read active slider values
        current_temp = self.temp_var.get()
        pid_demand = self.pid_var.get()
        valve_feedback = self.valve_var.get()
        valve_delta = abs(pid_demand - valve_feedback)

        # Update text labels cleanly next to their respective loops
        self.temp_lbl.config(text=f"Current: {current_temp:.1f} °C")
        self.pid_lbl.config(text=f"Demand: {pid_demand:.1f} %")
        self.valve_lbl.config(text=f"Feedback: {valve_feedback:.1f} %")
        self.stiction_lbl.config(text=f"Valve Delta: {valve_delta:.1f} %")

        # 1. Functional Safety Logic (OT Interlock Layer)
        if current_temp >= 120.0:
            self.sis_led.config(text="SIS TRIP: ACTIVE (OVERTEMP)", bg="#ff0000")
            # Emergency automated actions
            self.pid_var.set(0.0)
            self.valve_var.set(0.0)
        else:
            self.sis_led.config(text="SIS INTERLOCK: NORMAL", bg="#008000")

        # 2. Predictive Analytical Insights (IT Layer)
        if valve_delta > 15.0 and current_temp > 100.0:
            self.ai_box.config(text="⚠️ ANOMALY DETECTED!\nValve Stiction / Drift\nEstimated Trip: < 15 Mins", 
                               bg="#ff9900", fg="#000000")
        elif valve_delta > 15.0:
            self.ai_box.config(text="⚠️ WARNING\nHigh Valve Stiction Detected\nMonitor Reboiler Loops", 
                               bg="#ffff00", fg="#000000")
        else:
            self.ai_box.config(text="AI PREDICTIVE MAINTENANCE\nSignatures Nominal\nNo Anomalies Found", 
                               bg="#2d2d2d", fg="#ffffff")

if __name__ == "__main__":
    root = tk.Tk()
    app = DistillationHMI(root)
    root.mainloop()