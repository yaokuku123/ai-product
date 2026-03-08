# 通用视频下载工具

一个简单易用的命令行工具，可以从网页中提取并下载所有可用的视频。支持多种视频来源和格式，自动处理各种网页结构。

## 功能特点

- 🚀 自动分析网页结构，提取所有视频URL
- 🔍 支持多种提取方法：
  - 查找 `<video>` 标签
  - 解析 `<iframe>` 嵌入式视频
  - 识别包含视频链接的 `<a>` 标签
  - 从 JavaScript 代码中提取视频地址
- 📥 智能下载策略：
  - 优先使用 yt-dlp（支持 1000+ 网站）
  - 备用方案：直接下载视频文件
- 📝 简单的命令行界面，易于使用
- 💾 自动创建输出目录，文件名自动清理
- 🎯 支持直接下载单个视频URL

## 安装方法

### 前置依赖

需要安装 yt-dlp（自动通过pip安装），某些情况下可能需要ffmpeg：

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
choco install ffmpeg
```

### 安装工具

```bash
# 进入项目目录
cd tools/video_downloader

# 安装命令行工具（方便全局调用）
pip install -e .
```

## 使用方法

### 基本使用

```bash
# 下载网页中的所有视频到当前目录
video-downloader xxx

# 指定输出目录
video-downloader xxx -o ./downloads

# 直接下载单个视频URL
video-downloader xxx -o ./videos
```

### 可选参数

- `-o, --output-dir`: 指定输出目录（默认：当前目录）
- `-d, --debug`: 启用调试模式，保存页面内容以便分析（保存到 output_dir/debug/ 目录）
- `--help`: 显示帮助信息
- `--version`: 显示版本信息

## 支持的视频来源

- 普通视频文件（MP4、WebM、AVI、MOV、MKV等）
- HLS流媒体（.m3u8）
- YouTube、B站等视频网站（通过yt-dlp支持）
- 各种嵌入视频的网页

## 工作原理

1. **页面分析**：下载网页内容并解析DOM结构
2. **视频提取**：使用多种方法提取视频URL
3. **视频下载**：使用yt-dlp或直接下载获取视频文件
4. **保存文件**：自动命名和保存视频到指定目录

## 常见问题

### Q: 为什么没有找到视频？

A: 网页可能使用了动态加载或加密技术。可以使用 `-d, --debug` 参数启用调试模式，查看保存的页面内容并分析。

### Q: 工具下载了 HTML 而不是视频？

A: 新版本已经添加了内容类型验证，不会再下载 HTML 页面。如果仍然找不到视频，请使用调试模式分析页面结构。

### Q: 下载速度慢？

A: 取决于网络状况和服务器响应速度。可以尝试使用下载加速器。

### Q: 支持哪些视频格式？

A: 理论上支持所有常见视频格式，包括MP4、WebM、AVI、MOV、MKV、FLV等。

### Q: 如何使用调试模式？

A: 在命令中添加 `-d` 参数：
```bash
video-downloader https://example.com/page -d -o ./downloads
```
页面内容会保存到 `downloads/debug/page_content.html`，你可以查看这个文件来了解网页结构。

## 许可证

MIT
