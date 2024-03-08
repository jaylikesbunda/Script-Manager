import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import threading
import os

def create_styled_button(master, text, command):
    """Helper function to create a styled button with gradient look and rounded corners."""
    button = tk.Button(master, text=text, command=command,
                       bg="lightgrey", fg="black", bd=0,
                       highlightthickness=0, padx=10, pady=5)
    button.config(font=('Helvetica', 11, 'bold'))
    return button

class ScriptController:
    def __init__(self, master, filepath):
        self.filepath = filepath
        self.master = master
        self.process = None
        self.console_visible = False
        self.create_widgets()
        self.console_frame.pack_forget()  # Initially hide the console

    def create_widgets(self):
        self.main_frame = tk.Frame(self.master, bg='white', relief='solid', bd=1)
        self.main_frame.pack(fill=tk.X, padx=10, pady=5)

        # Display just the file name, not the full path
        file_name = os.path.basename(self.filepath)
        self.lbl_name = tk.Label(self.main_frame, text=file_name, bg='white', anchor="w")
        self.lbl_name.config(font=('Helvetica', 12))
        self.lbl_name.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        self.btn_start = create_styled_button(self.main_frame, "Start", self.start_script)
        self.btn_start.pack(side=tk.LEFT, padx=5)

        self.btn_stop = create_styled_button(self.main_frame, "Stop", self.stop_script)
        self.btn_stop.pack(side=tk.LEFT, padx=5)

        self.btn_restart = create_styled_button(self.main_frame, "Restart", self.restart_script)
        self.btn_restart.pack(side=tk.LEFT, padx=5)

        self.toggle_btn = create_styled_button(self.main_frame, "▼", self.toggle_console)
        self.toggle_btn.pack(side=tk.RIGHT, padx=5)

        self.lbl_status = tk.Label(self.main_frame, text="Status: Ready", bg='white')
        self.lbl_status.config(font=('Helvetica', 12))
        self.lbl_status.pack(side=tk.RIGHT, padx=10)

        # Console frame
        self.console_frame = tk.Frame(self.master, bg='white')
        self.console_text = scrolledtext.ScrolledText(self.console_frame, height=5, state='disabled')
        self.console_text.pack(fill=tk.BOTH, expand=True, padx=10)

    def toggle_console(self):
        self.console_visible = not self.console_visible
        if self.console_visible:
            self.console_frame.pack(fill=tk.X, padx=10, pady=5)
            self.toggle_btn.config(text="▲")
        else:
            self.console_frame.pack_forget()
            self.toggle_btn.config(text="▼")

    def update_console_log(self, text):
        self.console_text.configure(state='normal')
        self.console_text.insert(tk.END, text)
        self.console_text.configure(state='disabled')
        self.console_text.see(tk.END)

    def start_script(self):
        if self.process is None or self.process.poll() is not None:
            self.process = subprocess.Popen(["python", self.filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True)
            self.lbl_status.config(text="Status: Running")
            self.update_console_log(f"Started: {self.filepath}\n")
            threading.Thread(target=self.monitor_script, daemon=True).start()

    def stop_script(self):
        if self.process:
            self.process.terminate()
            self.process = None
            self.lbl_status.config(text="Status: Stopped")
            self.update_console_log(f"Stopped: {self.filepath}\n")

    def restart_script(self):
        self.stop_script()
        self.start_script()

    def monitor_script(self):
        while True:
            output = self.process.stdout.readline()
            if self.process.poll() is not None:
                if output == '':
                    break
                else:
                    self.update_console_log(output)
            elif output:
                self.update_console_log(output)
            else:
                break
        exit_code = self.process.poll()
        self.process = None
        if exit_code == 0:
            self.lbl_status.config(text="Status: Finished Successfully")
        else:
            self.lbl_status.config(text="Status: Error")
            self.update_console_log(f"Script {self.filepath} exited with error code {exit_code}\n")

class BotManagerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Discord Bot Manager")
        self.master.configure(bg='white')
        self.controllers = []
        self.initialize_ui()

    def initialize_ui(self):
        self.frame_buttons = tk.Frame(self.master, bg='white')
        self.frame_buttons.pack(pady=10)

        self.btn_load = create_styled_button(self.frame_buttons, "Load Script", self.load_script)
        self.btn_load.grid(row=0, column=0, padx=5, pady=5)

        self.update_window_size()

    def update_window_size(self):
        # Dynamically adjust the window size based on the number of loaded scripts
        base_height = 100  # Start with a height that can accommodate the 'Load Script' button
        height_per_script = 100  # Estimate a height per script and console area
        total_height = base_height + height_per_script * len(self.controllers)
        self.master.geometry(f"800x{total_height}")

    def load_script(self):
        filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if filepath:
            controller = ScriptController(self.master, filepath)
            self.controllers.append(controller)
            self.update_window_size()

if __name__ == "__main__":
    root = tk.Tk()
    app = BotManagerApp(root)
    root.mainloop()
