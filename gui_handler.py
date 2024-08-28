import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import tkinter.font as tkfont
import threading
import time
from typing import Any, Callable

class Tooltip:
    """Class to create tooltips for widgets"""
    def __init__(self, widget: tk.Widget, text: str):
        self.widget = widget
        self.text = text
        self.tooltip: tk.Toplevel = None
        self.widget.bind('<Enter>', self.show_tooltip)
        self.widget.bind('<Leave>', self.hide_tooltip)

    def show_tooltip(self, event: tk.Event = None) -> None:
        if self.tooltip:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, background="lightyellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event: tk.Event = None) -> None:
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class GUIHandler:
    def __init__(self, root: tk.Tk, app: Any):
        self.root = root
        self.app = app
        self.voice_response_enabled = tk.BooleanVar(value=True)
        self.stop_event = threading.Event()

        self.configure_root()
        self.create_widgets()

    def configure_root(self) -> None:
        """Configure the root window for the dark theme."""
        self.root.title("AI Assistant")
        self.root.configure(bg="#2B2B2B")
        self.root.geometry("1000x600")
        self.root.resizable(True, True)

    def create_widgets(self) -> None:
        """Create all GUI widgets and layout with a dark theme."""
        self._setup_fonts()
        self._create_query_frame()
        self._create_files_frame()
        self._create_result_text()

    def _setup_fonts(self) -> None:
        """Setup fonts for the GUI."""
        self.font = tkfont.Font(family="Helvetica", size=12)
        self.bold_font = tkfont.Font(family="Helvetica", size=12, weight="bold")
        self.large_font = tkfont.Font(family="Helvetica", size=14)

    def _create_button(self, parent: tk.Widget, text: str, command: Callable, tooltip_text: str) -> tk.Button:
        """Create a button with a tooltip."""
        button = tk.Button(parent, text=text, command=command, bg="#4A4A4A", fg="white", font=self.large_font)
        button.pack(side=tk.LEFT, padx=5)
        Tooltip(button, tooltip_text)
        return button

    def _create_query_frame(self) -> None:
        """Create the query input frame and its widgets."""
        self.query_frame = tk.Frame(self.root, bg="#2E2E2E")
        self.query_frame.pack(fill=tk.X, pady=10, padx=10)

        self._create_button(self.query_frame, "📎", self.select_files, "Select files to process")
        self._create_button(self.query_frame, "❌", self.remove_files, "Remove selected files")

        self.query_entry = tk.Entry(self.query_frame, width=50, font=self.large_font, bg="#3C3C3C", fg="white", insertbackground="white")
        self.query_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.query_entry.bind("<Return>", self.submit_query)

        self.voice_response_button = self._create_button(self.query_frame, "🔊", self.toggle_voice_response, "Toggle voice response on/off")
        self._create_button(self.query_frame, "🎤", self.use_microphone, "Use microphone for voice input")


    def _create_files_frame(self) -> None:
        """Create the frame for displaying attached files."""
        self.files_frame = tk.Frame(self.root, bg="#2B2B2B")
        self.files_frame.pack(fill=tk.X, pady=(0, 10), padx=10)

        self.attached_files_label = tk.Label(self.files_frame, text="Attached Files:", font=self.bold_font, bg="#2B2B2B", fg="white")
        self.attached_files_label.pack(anchor=tk.W)

        self.files_listbox = tk.Listbox(self.files_frame, font=self.font, bg="#3C3C3C", fg="white", selectbackground="#4A4A4A", height=4)
        self.files_listbox.pack(fill=tk.X, pady=5)

    def _create_result_text(self) -> None:
        """Create the text area for displaying results."""
        self.result_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=15, font=self.font, bg="#1E1E1E", fg="white", insertbackground='white', padx=10, pady=10)
        self.result_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def select_files(self) -> None:
        """Open a file dialog and load selected files."""
        file_paths = filedialog.askopenfilenames(
            title="Select files to process",
            filetypes=[("All files", "*.*")]
        )
        if file_paths:
            result = self.app.load_files(file_paths)
            self.update_files_listbox()
            messagebox.showinfo("Info", result)

    def remove_files(self) -> None:
        """Remove selected files."""
        selected_files = [self.files_listbox.get(i) for i in self.files_listbox.curselection()]
        if not selected_files:
            messagebox.showwarning("Warning", "No files selected to remove.")
            return
        result = self.app.remove_files(selected_files)
        self.update_files_listbox()
        messagebox.showinfo("Info", result)

    def update_files_listbox(self) -> None:
        """Update the Listbox to display the attached files."""
        self.files_listbox.delete(0, tk.END)
        for file_path in self.app.file_paths:
            self.files_listbox.insert(tk.END, file_path)

    def submit_query(self, event: tk.Event = None) -> None:
        """Handle the query submission and respond."""
        question = self.query_entry.get().strip()

        if not question:
            messagebox.showwarning("Warning", "Please enter a question.")
            return

        self.stop_event.clear()
        response_thread = threading.Thread(target=self.process_query, args=(question,))
        response_thread.start()

    def process_query(self, question: str) -> None:
        """Process the query and handle the response."""
        response = self.app.handle_query(question)
        if not self.stop_event.is_set():
            self.stream_text(response)
            if not self.stop_event.is_set():
                time.sleep(2)
                error = self.app.respond(response, self.voice_response_enabled.get())
                if error:
                    messagebox.showwarning("Warning", error)

    def stream_text(self, response: str) -> None:
        """Display the response text incrementally."""
        self.result_text.delete(1.0, tk.END)
        chunk_size = 100
        for i in range(0, len(response), chunk_size):
            if self.stop_event.is_set():
                break
            self.result_text.insert(tk.END, response[i:i+chunk_size])
            self.result_text.yview(tk.END)
            time.sleep(0.1)

    def use_microphone(self) -> None:
        """Handle microphone input."""
        question = self.app.voice_assistant.get_query() if self.app.voice_assistant else ""
        if question:
            self.query_entry.delete(0, tk.END)
            self.query_entry.insert(0, question)
            self.submit_query()
        else:
            messagebox.showwarning("Warning", "No Microphone detected or input not recognized.")

    def toggle_voice_response(self) -> None:
        """Toggle the voice response feature on or off."""
        self.voice_response_enabled.set(not self.voice_response_enabled.get())
        
        # Update button text and color based on the state
        if self.voice_response_enabled.get():
            new_text = "🔊"  # Speaker with sound for "On"
            new_bg = "#4CAF50"  # Green for "On"
        else:
            new_text = "🔇"  # Muted speaker for "Off"
            new_bg = "#F44336"  # Red for "Off"

        self.voice_response_button.config(text=new_text, bg=new_bg)
