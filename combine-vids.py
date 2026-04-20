import os
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox


class CombineVideosApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Combine Videos")
        self.geometry("640x460")
        self.resizable(False, False)

        self.file_paths = []
        self.output_folder = tk.StringVar(value=os.getcwd())
        self.output_filename = tk.StringVar(value="output.mp4")

        self._build_ui()

    def _build_ui(self):
        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", padx=12, pady=(12, 6))

        add_button = tk.Button(button_frame, text="Add Files...", width=14, command=self.add_files)
        add_button.pack(side="left")

        remove_button = tk.Button(button_frame, text="Remove Selected", width=16, command=self.remove_selected)
        remove_button.pack(side="left", padx=(8, 0))

        clear_button = tk.Button(button_frame, text="Clear All", width=12, command=self.clear_files)
        clear_button.pack(side="left", padx=(8, 0))

        list_frame = tk.LabelFrame(self, text="Selected Files")
        list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.listbox = tk.Listbox(list_frame, selectmode="extended", activestyle="none",
                                  height=12, borderwidth=0, relief="flat")
        self.listbox.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)

        scrollbar = tk.Scrollbar(list_frame, command=self.listbox.yview)
        scrollbar.pack(side="left", fill="y", padx=(0, 8), pady=8)
        self.listbox.config(yscrollcommand=scrollbar.set)

        output_frame = tk.LabelFrame(self, text="Output")
        output_frame.pack(fill="x", padx=12, pady=(0, 12))

        folder_label = tk.Label(output_frame, text="Output Folder:")
        folder_label.grid(row=0, column=0, sticky="w", padx=8, pady=(10, 4))

        folder_entry = tk.Entry(output_frame, textvariable=self.output_folder, width=60)
        folder_entry.grid(row=1, column=0, sticky="we", padx=8)

        browse_button = tk.Button(output_frame, text="Browse...", command=self.browse_output_folder)
        browse_button.grid(row=1, column=1, sticky="e", padx=8)

        name_label = tk.Label(output_frame, text="Output Filename:")
        name_label.grid(row=2, column=0, sticky="w", padx=8, pady=(10, 4))

        name_entry = tk.Entry(output_frame, textvariable=self.output_filename, width=40)
        name_entry.grid(row=3, column=0, sticky="w", padx=8, pady=(0, 8))

        output_frame.columnconfigure(0, weight=1)

        action_frame = tk.Frame(self)
        action_frame.pack(fill="x", padx=12, pady=(0, 12))

        combine_button = tk.Button(action_frame, text="Combine Videos", bg="#4CAF50", fg="white",
                                   font=(None, 10, "bold"), command=self.combine_videos)
        combine_button.pack(side="left", padx=(0, 4))

        open_button = tk.Button(action_frame, text="Open Output Folder", command=self.open_output_folder)
        open_button.pack(side="left", padx=(8, 0))

        self.status_label = tk.Label(self, text="Select two or more video files and choose an output folder.", anchor="w")
        self.status_label.pack(fill="x", padx=12)

    def add_files(self):
        paths = filedialog.askopenfilenames(
            title="Select video files",
            filetypes=[
                ("Video files", "*.mp4 *.mov *.mkv *.avi *.flv *.wmv"),
                ("All files", "*")
            ],
        )
        if not paths:
            return
        self.file_paths.extend(paths)
        self._refresh_listbox()

    def remove_selected(self):
        selected = list(self.listbox.curselection())
        if not selected:
            return
        for index in reversed(selected):
            del self.file_paths[index]
        self._refresh_listbox()

    def clear_files(self):
        self.file_paths.clear()
        self._refresh_listbox()

    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="Select output folder", initialdir=self.output_folder.get())
        if folder:
            self.output_folder.set(folder)

    def open_output_folder(self):
        folder = self.output_folder.get().strip()
        if folder and os.path.isdir(folder):
            if sys.platform.startswith("win"):
                os.startfile(folder)
            elif sys.platform.startswith("darwin"):
                subprocess.run(["open", folder])
            else:
                subprocess.run(["xdg-open", folder])

    def _refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for path in self.file_paths:
            self.listbox.insert(tk.END, path)
        self.status_label.config(text=f"{len(self.file_paths)} files selected.")

    def combine_videos(self):
        if len(self.file_paths) < 2:
            messagebox.showwarning("Need more files", "Please select at least two video files to combine.")
            return

        output_folder = self.output_folder.get().strip()
        if not output_folder:
            messagebox.showwarning("Output folder required", "Please choose an output folder.")
            return
        if not os.path.isdir(output_folder):
            messagebox.showerror("Invalid folder", "The selected output folder does not exist.")
            return

        output_filename = self.output_filename.get().strip()
        if not output_filename:
            messagebox.showwarning("Filename required", "Please enter an output filename.")
            return

        output_path = os.path.join(output_folder, output_filename)
        if os.path.exists(output_path):
            if not messagebox.askyesno("Overwrite file?", f"The file '{output_filename}' already exists. Overwrite?"):
                return

        if not self._ffmpeg_available():
            messagebox.showerror("ffmpeg not found", "ffmpeg must be installed and available in your PATH.")
            return

        temp_path = None
        try:
            self.status_label.config(text="Building concat file list...")
            self.update_idletasks()
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as temp_file:
                for path in self.file_paths:
                    normalized = path.replace("\\", "/")
                    temp_file.write(f"file '{normalized}'\n")
                temp_path = temp_file.name

            command = [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                temp_path,
                "-c",
                "copy",
                output_path,
            ]

            self.status_label.config(text="Running ffmpeg... Please wait.")
            self.update_idletasks()
            result = subprocess.run(command, capture_output=True, text=True)
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

        if result.returncode != 0:
            self.status_label.config(text="Failed to combine videos.")
            messagebox.showerror("Combine failed", result.stderr or "ffmpeg failed.")
            return

        self.status_label.config(text=f"Successfully created: {output_path}")
        messagebox.showinfo("Success", f"Combined video saved to:\n{output_path}")

    def _ffmpeg_available(self):
        try:
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False


if __name__ == "__main__":
    app = CombineVideosApp()
    app.mainloop()