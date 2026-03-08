# B站视频文本提取工具

一个简单易用的命令行工具，可以提取B站视频的文本内容。优先下载视频字幕，如果没有字幕则自动下载音频并使用OpenAI Whisper进行语音转文字。

## 功能特点

- 🚀 优先下载原视频字幕，速度快，准确率高
- 🎤 无字幕时自动下载音频，使用Whisper模型进行语音识别
- 📝 支持多种输出格式，默认直接输出纯文本
- 💻 简单的命令行界面，易于使用
- 🔄 自动清理临时文件，不占用额外空间

## 安装方法

### 前置依赖

首先需要安装ffmpeg：
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
# 克隆项目到本地
git clone <repository-url>
cd deepsearch-fire

# 安装依赖
pip install -r requirements.txt

# 安装命令行工具（可选，方便全局调用）
pip install -e .
```

## 使用方法

### 基本使用

```bash
# 直接处理视频，输出文本到控制台
bilibili-text https://www.bilibili.com/video/BV1xx411c7mZ

# 保存文本到文件
bilibili-text https://www.bilibili.com/video/BV1xx411c7mZ -o output.txt
```

### 可选参数

- `-m, --model`: 指定Whisper模型大小，可选值：`tiny`, `base`, `small`, `medium`, `large`，默认是`base`
  ```bash
  # 使用更大的模型提高识别准确率
  bilibili-text https://www.bilibili.com/video/BV1xx411c7mZ -m small
  ```

- `-o, --output`: 指定输出文件路径

## 模型说明

Whisper模型会在第一次使用时自动下载，模型大小对应关系：
- tiny: ~1GB
- base: ~1GB
- small: ~2GB
- medium: ~5GB
- large: ~10GB

模型越大，识别准确率越高，但需要更多的内存和处理时间。对于中文视频，推荐使用`small`或以上模型获得更好的效果。

## 常见问题

### Q: 下载字幕失败怎么办？
A: 工具会自动 fallback 到下载音频进行语音识别，无需额外操作。

### Q: 第一次运行很慢？
A: 第一次使用时会自动下载Whisper模型，下载完成后后续运行就会很快了。

### Q: 支持哪些类型的B站视频？
A: 支持大部分公开的B站视频，包括普通视频、分P视频等。

## 许可证

MIT
