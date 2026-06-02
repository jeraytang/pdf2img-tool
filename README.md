# PDF2IMG Tool

一个基于 Tkinter + PyMuPDF 的 Windows 桌面小工具，用于将 PDF 按页批量转换为 PNG 图片。

## 功能特性

- 图形界面操作，免命令行使用
- 支持选择 PDF 文件和输出目录
- 支持 DPI 调整（72-600，默认 150）
- 后台线程转换，界面不卡顿
- 自动显示转换进度与状态提示
- 输出文件按页命名：`page_001.png`、`page_002.png`...

## 运行环境

- Python 3.8+
- Windows（已内置 `run.bat` / `build.bat`）

## 安装依赖

```bash
python -m pip install -r requirements.txt
```

当前依赖：

```txt
pymupdf>=1.24.0
```

## 启动方式

方式 1（推荐，跨平台）：

```bash
python main.py
```

方式 2（Windows 脚本）：

```bat
run.bat
```

## 使用步骤

1. 点击“选择 PDF”选择源文件。
2. 点击“选择目录”选择输出目录。
3. 设置 DPI（建议 150-300）。
4. 点击“开始转换”。
5. 转换完成后，图片输出在：`输出目录/<PDF文件名>_images/`。

## 打包 EXE

项目自带打包脚本：

```bat
build.bat
```

打包成功后可执行文件在：

```txt
dist/pdf2img.exe
```

说明：`build.bat` 会自动安装/更新依赖，并调用 PyInstaller 打包为单文件、无控制台窗口的 GUI 程序。

## 项目结构

```txt
pdf2img-tool/
├─ main.py
├─ requirements.txt
├─ run.bat
├─ build.bat
└─ src/
   └─ pdf2img/
      ├─ __init__.py
      └─ app.py
```

## 常见问题

### 1) 启动提示缺少 `fitz` / `pymupdf`

执行：

```bash
python -m pip install -r requirements.txt
```

### 2) 转换失败或输出为空

- 检查 PDF 是否损坏或加密。
- 检查输出目录是否有写入权限。
- 尝试降低 DPI（例如 150）后重试。

### 3) 打包失败

- 先确认 Python 与 pip 可用。
- 手动执行：`python -m pip install -r requirements.txt pyinstaller`
- 再次运行：`build.bat`

## License

This project is licensed under AGPL-3.0. See [LICENSE](LICENSE) file.

**Note:** This project uses [PyMuPDF](https://github.com/pymupdf/pymupdf) 
which is also licensed under AGPL-3.0.
