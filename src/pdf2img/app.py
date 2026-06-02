import os
import threading
import tkinter as tk
from queue import Empty, Queue
from tkinter import filedialog, messagebox, ttk

try:
    import fitz  # PyMuPDF
except Exception:  # pragma: no cover
    fitz = None


class PDFToImageApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PDF 转 PNG 工具")
        self.root.geometry("700x340")
        self.root.minsize(680, 320)

        self.pdf_path_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.dpi_var = tk.IntVar(value=150)
        self.status_var = tk.StringVar(value="请选择 PDF 文件和输出目录")
        self.progress_var = tk.DoubleVar(value=0.0)

        self._queue: Queue = Queue()
        self._converting = False

        self._build_ui()
        self._poll_queue()

        if fitz is None:
            self.status_var.set("未检测到 PyMuPDF，请先执行: pip install pymupdf")
            self.convert_btn.configure(state=tk.DISABLED)

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(container, text="PDF 转 PNG（Windows）", font=("Segoe UI", 14, "bold"))
        title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        ttk.Label(container, text="PDF 文件:").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Entry(container, textvariable=self.pdf_path_var).grid(row=1, column=1, sticky="ew", padx=8)
        ttk.Button(container, text="选择 PDF", command=self.select_pdf).grid(row=1, column=2, sticky="ew")

        ttk.Label(container, text="输出目录:").grid(row=2, column=0, sticky="w", pady=6)
        ttk.Entry(container, textvariable=self.output_dir_var).grid(row=2, column=1, sticky="ew", padx=8)
        ttk.Button(container, text="选择目录", command=self.select_output_dir).grid(row=2, column=2, sticky="ew")

        ttk.Label(container, text="DPI:").grid(row=3, column=0, sticky="w", pady=6)
        dpi_spin = ttk.Spinbox(container, from_=72, to=600, textvariable=self.dpi_var, width=10)
        dpi_spin.grid(row=3, column=1, sticky="w", padx=8)

        self.convert_btn = ttk.Button(container, text="开始转换", command=self.start_convert)
        self.convert_btn.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(16, 8))

        progress = ttk.Progressbar(
            container,
            variable=self.progress_var,
            maximum=100,
            orient="horizontal",
            mode="determinate",
        )
        progress.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(8, 6))

        status = ttk.Label(container, textvariable=self.status_var)
        status.grid(row=6, column=0, columnspan=3, sticky="w", pady=(6, 0))

        container.columnconfigure(1, weight=1)
        container.columnconfigure(2, minsize=110)

    def select_pdf(self) -> None:
        path = filedialog.askopenfilename(
            title="选择 PDF 文件",
            filetypes=[("PDF 文件", "*.pdf"), ("全部文件", "*.*")],
        )
        if path:
            self.pdf_path_var.set(path)
            if not self.output_dir_var.get().strip():
                self.output_dir_var.set(os.path.dirname(path))

    def select_output_dir(self) -> None:
        path = filedialog.askdirectory(title="选择输出目录")
        if path:
            self.output_dir_var.set(path)

    def start_convert(self) -> None:
        if self._converting:
            return

        pdf_path = self.pdf_path_var.get().strip()
        output_dir = self.output_dir_var.get().strip()

        if fitz is None:
            messagebox.showerror("缺少依赖", "未安装 PyMuPDF，请先执行: pip install pymupdf")
            return

        if not pdf_path:
            messagebox.showwarning("参数不完整", "请先选择 PDF 文件")
            return

        if not os.path.isfile(pdf_path):
            messagebox.showerror("文件不存在", "选择的 PDF 文件不存在")
            return

        if not output_dir:
            messagebox.showwarning("参数不完整", "请先选择输出目录")
            return

        try:
            dpi = int(self.dpi_var.get())
            if dpi < 72 or dpi > 600:
                raise ValueError
        except Exception:
            messagebox.showerror("DPI 无效", "DPI 必须是 72 到 600 之间的整数")
            return

        os.makedirs(output_dir, exist_ok=True)

        self._converting = True
        self.convert_btn.configure(state=tk.DISABLED)
        self.progress_var.set(0)
        self.status_var.set("开始转换...")

        worker = threading.Thread(
            target=self._convert_pdf,
            args=(pdf_path, output_dir, dpi),
            daemon=True,
        )
        worker.start()

    def _convert_pdf(self, pdf_path: str, output_dir: str, dpi: int) -> None:
        try:
            doc = fitz.open(pdf_path)
            total = len(doc)

            if total == 0:
                self._queue.put(("error", "PDF 没有可转换页面"))
                return

            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            target_dir = os.path.join(output_dir, f"{base_name}_images")
            os.makedirs(target_dir, exist_ok=True)

            for i, page in enumerate(doc, start=1):
                pix = page.get_pixmap(dpi=dpi)
                file_name = f"page_{i:03d}.png"
                file_path = os.path.join(target_dir, file_name)
                pix.save(file_path)

                percent = (i / total) * 100
                self._queue.put(("progress", percent, i, total, file_path))

            self._queue.put(("done", target_dir, total))
        except Exception as exc:
            self._queue.put(("error", f"转换失败: {exc}"))

    def _poll_queue(self) -> None:
        try:
            while True:
                msg = self._queue.get_nowait()
                self._handle_message(msg)
        except Empty:
            pass
        self.root.after(100, self._poll_queue)

    def _handle_message(self, msg: tuple) -> None:
        kind = msg[0]

        if kind == "progress":
            _, percent, cur, total, _ = msg
            self.progress_var.set(percent)
            self.status_var.set(f"正在转换: 第 {cur}/{total} 页")
            return

        if kind == "done":
            _, target_dir, total = msg
            self._converting = False
            self.convert_btn.configure(state=tk.NORMAL)
            self.progress_var.set(100)
            self.status_var.set(f"完成: 共 {total} 页，输出目录: {target_dir}")
            messagebox.showinfo("转换完成", f"已输出 {total} 张图片\n{target_dir}")
            return

        if kind == "error":
            _, text = msg
            self._converting = False
            self.convert_btn.configure(state=tk.NORMAL)
            self.status_var.set(text)
            messagebox.showerror("错误", text)


def main() -> None:
    root = tk.Tk()
    app = PDFToImageApp(root)
    root.mainloop()
