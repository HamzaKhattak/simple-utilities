from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox


VIDEO_FILETYPES = [
	("Video files", "*.mp4 *.mov *.mkv *.avi *.flv *.wmv *.m4v *.ts"),
	("All files", "*.*"),
]


class CombineVideosApp(tk.Tk):
	def __init__(self) -> None:
		super().__init__()
		self.title("Combine Videos")
		self.geometry("760x520")
		self.minsize(760, 520)

		self.file_paths: list[str] = []
		self.output_folder = tk.StringVar(value=str(Path.cwd()))
		self.output_filename = tk.StringVar(value="combined.mp4")

		self._build_ui()
		self._set_status("Select at least two video files in the order they should be combined.")

	def _build_ui(self) -> None:
		controls = tk.Frame(self)
		controls.pack(fill="x", padx=12, pady=(12, 8))

		tk.Button(controls, text="Add Files...", width=14, command=self.add_files).pack(side="left")
		tk.Button(controls, text="Remove Selected", width=16, command=self.remove_selected).pack(side="left", padx=(8, 0))
		tk.Button(controls, text="Clear All", width=12, command=self.clear_files).pack(side="left", padx=(8, 0))
		tk.Button(controls, text="Move Up", width=10, command=self.move_up).pack(side="left", padx=(16, 0))
		tk.Button(controls, text="Move Down", width=10, command=self.move_down).pack(side="left", padx=(8, 0))

		list_frame = tk.LabelFrame(self, text="Video Files")
		list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

		self.listbox = tk.Listbox(
			list_frame,
			selectmode="extended",
			activestyle="none",
			borderwidth=0,
			relief="flat",
			exportselection=False,
		)
		self.listbox.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)

		scrollbar = tk.Scrollbar(list_frame, command=self.listbox.yview)
		scrollbar.pack(side="left", fill="y", padx=(0, 8), pady=8)
		self.listbox.config(yscrollcommand=scrollbar.set)

		output_frame = tk.LabelFrame(self, text="Output")
		output_frame.pack(fill="x", padx=12, pady=(0, 12))
		output_frame.columnconfigure(0, weight=1)

		tk.Label(output_frame, text="Output Folder:").grid(row=0, column=0, sticky="w", padx=8, pady=(10, 4))
		tk.Entry(output_frame, textvariable=self.output_folder).grid(row=1, column=0, sticky="we", padx=8)
		tk.Button(output_frame, text="Browse...", command=self.browse_output_folder).grid(row=1, column=1, sticky="e", padx=8)

		tk.Label(output_frame, text="Output Filename:").grid(row=2, column=0, sticky="w", padx=8, pady=(10, 4))
		tk.Entry(output_frame, textvariable=self.output_filename, width=40).grid(row=3, column=0, sticky="w", padx=8, pady=(0, 10))

		actions = tk.Frame(self)
		actions.pack(fill="x", padx=12, pady=(0, 8))

		tk.Button(actions, text="Combine Videos", width=18, command=self.combine_videos).pack(side="left")
		tk.Button(actions, text="Open Output Folder", width=18, command=self.open_output_folder).pack(side="left", padx=(8, 0))

		self.status_label = tk.Label(self, anchor="w")
		self.status_label.pack(fill="x", padx=12, pady=(0, 12))

	def _set_status(self, message: str) -> None:
		self.status_label.config(text=message)
		self.update_idletasks()

	def add_files(self) -> None:
		paths = filedialog.askopenfilenames(title="Select video files", filetypes=VIDEO_FILETYPES)
		if not paths:
			return

		self.file_paths.extend(paths)
		self._refresh_listbox()

	def remove_selected(self) -> None:
		selected = list(self.listbox.curselection())
		if not selected:
			return

		for index in reversed(selected):
			del self.file_paths[index]
		self._refresh_listbox()

	def clear_files(self) -> None:
		if not self.file_paths:
			return

		self.file_paths.clear()
		self._refresh_listbox()

	def move_up(self) -> None:
		selected = list(self.listbox.curselection())
		if not selected or selected[0] == 0:
			return

		for index in selected:
			self.file_paths[index - 1], self.file_paths[index] = self.file_paths[index], self.file_paths[index - 1]

		self._refresh_listbox(selected=[index - 1 for index in selected])

	def move_down(self) -> None:
		selected = list(self.listbox.curselection())
		if not selected or selected[-1] == len(self.file_paths) - 1:
			return

		for index in reversed(selected):
			self.file_paths[index + 1], self.file_paths[index] = self.file_paths[index], self.file_paths[index + 1]

		self._refresh_listbox(selected=[index + 1 for index in selected])

	def browse_output_folder(self) -> None:
		folder = filedialog.askdirectory(title="Select output folder", initialdir=self.output_folder.get())
		if folder:
			self.output_folder.set(folder)

	def open_output_folder(self) -> None:
		folder = self.output_folder.get().strip()
		if not folder:
			messagebox.showwarning("Missing output folder", "Choose an output folder first.")
			return

		if not os.path.isdir(folder):
			messagebox.showerror("Invalid output folder", "The selected output folder does not exist.")
			return

		if sys.platform.startswith("win"):
			os.startfile(folder)
		elif sys.platform.startswith("darwin"):
			subprocess.run(["open", folder], check=False)
		else:
			subprocess.run(["xdg-open", folder], check=False)

	def _refresh_listbox(self, selected: list[int] | None = None) -> None:
		self.listbox.delete(0, tk.END)
		for index, path in enumerate(self.file_paths, start=1):
			self.listbox.insert(tk.END, f"{index:02d}. {path}")

		if selected:
			for index in selected:
				self.listbox.selection_set(index)

		if self.file_paths:
			self._set_status(f"{len(self.file_paths)} files selected. The list order is the combine order.")
		else:
			self._set_status("Select at least two video files in the order they should be combined.")

	def combine_videos(self) -> None:
		if len(self.file_paths) < 2:
			messagebox.showwarning("Need more files", "Select at least two video files to combine.")
			return

		output_dir = self.output_folder.get().strip()
		if not output_dir:
			messagebox.showwarning("Output folder required", "Choose an output folder.")
			return

		output_folder = Path(output_dir)
		if not output_folder.is_dir():
			messagebox.showerror("Invalid output folder", "The selected output folder does not exist.")
			return

		output_name = self.output_filename.get().strip()
		if not output_name:
			messagebox.showwarning("Filename required", "Enter an output filename.")
			return

		output_path = output_folder / output_name
		if output_path.exists():
			should_overwrite = messagebox.askyesno(
				"Overwrite file?",
				f"{output_path.name} already exists in the selected folder. Overwrite it?",
			)
			if not should_overwrite:
				return

		if not self._ffmpeg_available():
			messagebox.showerror("ffmpeg not found", "ffmpeg must be installed and available on PATH.")
			return

		concat_file = None
		try:
			self._set_status("Preparing ffmpeg concat list...")
			concat_file = self._build_concat_file()
			command = [
				"ffmpeg",
				"-y",
				"-f",
				"concat",
				"-safe",
				"0",
				"-i",
				concat_file,
				"-c",
				"copy",
				str(output_path),
			]

			self._set_status("Running ffmpeg...")
			result = subprocess.run(command, capture_output=True, text=True)
		finally:
			if concat_file:
				try:
					os.remove(concat_file)
				except OSError:
					pass

		if result.returncode != 0:
			self._set_status("Combine failed.")
			error_message = result.stderr.strip() or result.stdout.strip() or "ffmpeg failed to combine the files."
			messagebox.showerror("Combine failed", error_message)
			return

		self._set_status(f"Created {output_path}")
		messagebox.showinfo("Success", f"Combined video saved to:\n{output_path}")

	def _build_concat_file(self) -> str:
		with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as handle:
			for path in self.file_paths:
				escaped_path = Path(path).as_posix().replace("'", r"'\\''")
				handle.write(f"file '{escaped_path}'\n")
			return handle.name

	@staticmethod
	def _ffmpeg_available() -> bool:
		try:
			result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
		except FileNotFoundError:
			return False
		return result.returncode == 0


def main() -> None:
	app = CombineVideosApp()
	app.mainloop()


if __name__ == "__main__":
	main()
