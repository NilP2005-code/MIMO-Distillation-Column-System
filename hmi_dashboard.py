import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import tkinter as tk
from tkinter import ttk
import random
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# --- 1. LIVE SCIKIT-LEARN PIPELINE FOR ANOMALY DIAGNOSTICS ---
# Historical logbook training data (Normal operating states vs. Valve Stiction)
training_data = {
    'Temperature': [78.5, 80.2, 82.1, 115.4, 119.8, 79.1, 114.5, 83.0],
    'Pressure':    [1.2,  1.2,  1.3,  2.1,   2.4,   1.2,  2.0,   1.3],
    'Steam_Flow':  [40.1, 41.5, 42.5, 95.2,  98.6,  39.8, 92.0,  44.0],
    'Anomaly':     [0,    0,    0,    1,     1,     0,    1,     0]
}
df = pd.DataFrame(training_data)
X = df[['Temperature', 'Pressure', 'Steam_Flow']]
y = df['Anomaly']

# Train the model live at control room startup
ml_model = RandomForestClassifier(n_estimators=10, random_state=42)
ml_model.fit(X, y)

# --- 2. GUI SYSTEM ARCHITECTURE ---
root = tk.Tk()
root.title("Distillation Column Control Room - Operator HMI")
root.geometry("550x480")
root.configure(bg="#2b2b2b")

temp, pressure, steam, valve_fault = 78.5, 1.2, 40.0, False

def trigger_fault():
    global valve_fault
    valve_fault = True
    fault_btn.config(text="⚠️ FAULT INJECTED", state="disabled", bg="#e74c3c")

def update_plant():
    global temp, pressure, steam, valve_fault
    
    if valve_fault:
        temp += 4.5
        pressure += 0.15
        steam = 95.0
    else:
        temp = max(75.0, min(85.0, temp + random.uniform(-0.5, 0.5)))
        pressure = max(1.0, min(1.5, pressure + random.uniform(-0.02, 0.02)))
        steam = max(38.0, min(42.0, steam + random.uniform(-0.4, 0.4)))

    # --- REAL-TIME AI MODEL INFERENCE ---
    live_telemetry = [[temp, pressure, steam]]
    ai_prediction = ml_model.predict(live_telemetry)[0]

    # --- SAFETY INSTRUMENTED SYSTEM (SIS) INTERLOCK ---
    if temp >= 120.0:
        sis_label.config(text="🚨 SIS INTERLOCK TRIPPED\nEMERGENCY SHUTDOWN ACTIVE", bg="#e74c3c", fg="white")
        temp, pressure, steam = 65.0, 1.0, 0.0
        valve_fault = False
        fault_btn.config(text="Inject Steam Valve Fault", state="normal", bg="#f39c12")
    elif ai_prediction == 1:
        sis_label.config(text="⚠️ AI PREDICTIVE ALERT: ANOMALOUS STICTION\nSIS TRIP PROBABLE WITHIN 15 MINUTES", bg="#d35400", fg="white")
    else:
        sis_label.config(text="SYSTEM STATUS: NORMAL\nBPCS PID LOOPS STABLE", bg="#27ae60", fg="white")

    temp_var.set(f"{temp:.1f} °C")
    temp_progress['value'] = temp
    press_var.set(f"{pressure:.2f} Bar")
    steam_var.set(f"{steam:.1f} %")
    
    root.after(100, update_plant)

# --- GUI WIDGET DESIGN ---
tk.Label(root, text="MAIN OPERATIONS DESK: REFINERY COLUMN 4", font=("Arial", 12, "bold"), fg="#ffffff", bg="#2b2b2b").pack(pady=15)
sis_label = tk.Label(root, text="SYSTEM STATUS: INITIALIZING", font=("Arial", 10, "bold"), width=50, height=2, bd=2, relief="sunken")
sis_label.pack(pady=5)

frame = tk.Frame(root, bg="#333333", padx=15, pady=15, bd=1, relief="solid")
frame.pack(pady=10, fill="x", padx=30)

tk.Label(frame, text="Column Temperature:", font=("Arial", 10), fg="white", bg="#333333").grid(row=0, column=0, sticky="w")
temp_var = tk.StringVar()
tk.Label(frame, textvariable=temp_var, font=("Arial", 11, "bold"), fg="#5dade2", bg="#333333").grid(row=0, column=1, sticky="e", padx=20)
temp_progress = ttk.Progressbar(frame, orient="horizontal", length=400, mode="determinate", maximum=140)
temp_progress.grid(row=1, column=0, columnspan=2, pady=10)

metrics_frame = tk.Frame(root, bg="#2b2b2b")
metrics_frame.pack(pady=5)
tk.Label(metrics_frame, text="Pressure: ", font=("Arial", 10), fg="white", bg="#2b2b2b").grid(row=0, column=0)
press_var = tk.StringVar()
tk.Label(metrics_frame, textvariable=press_var, font=("Arial", 10, "bold"), fg="#2ecc71", bg="#2b2b2b").grid(row=0, column=1, padx=10)
tk.Label(metrics_frame, text="Steam Flow: ", font=("Arial", 10), fg="white", bg="#2b2b2b").grid(row=0, column=2, padx=10)
steam_var = tk.StringVar()
tk.Label(metrics_frame, textvariable=steam_var, font=("Arial", 10, "bold"), fg="#f1c40f", bg="#2b2b2b").grid(row=0, column=3)

fault_btn = tk.Button(root, text="Inject Steam Valve Fault", font=("Arial", 11, "bold"), bg="#f39c12", fg="white", width=25, command=trigger_fault)
fault_btn.pack(pady=15)

root.after(100, update_plant)
root.mainloop()
