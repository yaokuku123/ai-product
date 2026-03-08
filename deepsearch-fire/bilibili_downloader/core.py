import os
import tempfile
import yt_dlp
from faster_whisper import WhisperModel
import ffmpeg

class BilibiliProcessor:
    def __init__(self, whisper_model: str = "base"):
        """
        初始化B站视频处理器
        :param whisper_model: Whisper模型大小，可选：tiny, base, small, medium, large
        """
        self.whisper_model = whisper_model
        self.whisper_instance = None

    def _load_whisper(self):
        """延迟加载Whisper模型"""
        if self.whisper_instance is None:
            # 使用faster-whisper，自动检测CPU/GPU，使用int8量化提高速度
            self.whisper_instance = WhisperModel(
                self.whisper_model,
                device="auto",
                compute_type="int8"
            )

    def download_subtitle(self, url: str, output_dir: str = None) -> str:
        """
        尝试下载B站视频字幕
        :param url: B站视频链接
        :param output_dir: 输出目录，默认临时目录
        :return: 字幕文件路径，如果没有字幕返回None
        """
        if output_dir is None:
            output_dir = tempfile.gettempdir()

        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['zh', 'zh-CN', 'en'],
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                video_id = info['id']

                # 查找下载的字幕文件
                for ext in ['.vtt', '.srt', '.ass']:
                    subtitle_path = os.path.join(output_dir, f"{video_id}.zh{ext}")
                    if os.path.exists(subtitle_path):
                        return subtitle_path
                    subtitle_path = os.path.join(output_dir, f"{video_id}.zh-CN{ext}")
                    if os.path.exists(subtitle_path):
                        return subtitle_path

                return None
            except Exception as e:
                print(f"下载字幕失败: {str(e)}")
                return None

    def download_audio(self, url: str, output_dir: str = None) -> str:
        """
        下载B站视频音频
        :param url: B站视频链接
        :param output_dir: 输出目录，默认临时目录
        :return: 音频文件路径
        """
        if output_dir is None:
            output_dir = tempfile.gettempdir()

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            audio_path = os.path.join(output_dir, f"{video_id}.mp3")
            return audio_path

    def audio_to_text(self, audio_path: str) -> str:
        """
        将音频转换为文本
        :param audio_path: 音频文件路径
        :return: 识别的文本内容
        """
        self._load_whisper()
        segments, _ = self.whisper_instance.transcribe(audio_path, language='zh')
        return '\n'.join([segment.text.strip() for segment in segments])

    def process_video(self, url: str, output_file: str = None) -> str:
        """
        处理B站视频：优先下载字幕，没有字幕则下载音频转文字
        :param url: B站视频链接
        :param output_file: 输出文本文件路径，如果为None则只返回文本
        :return: 识别的文本内容
        """
        # 首先尝试下载字幕
        print("正在尝试下载字幕...")
        subtitle_path = self.download_subtitle(url)

        if subtitle_path:
            print("找到字幕文件，正在提取文本...")
            # 读取字幕文件内容
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 简单处理字幕文件，去除时间戳等格式信息
            if subtitle_path.endswith('.vtt') or subtitle_path.endswith('.srt'):
                lines = content.split('\n')
                text_lines = []
                for line in lines:
                    line = line.strip()
                    # 跳过空行、时间轴行、序号行
                    if not line:
                        continue
                    if '-->' in line:
                        continue
                    if line.isdigit():
                        continue
                    text_lines.append(line)
                text = '\n'.join(text_lines)
            else:
                text = content

            # 清理临时字幕文件
            os.unlink(subtitle_path)
        else:
            print("没有找到字幕，正在下载音频...")
            # 下载音频
            audio_path = self.download_audio(url)
            print("正在将音频转换为文本...")
            text = self.audio_to_text(audio_path)
            # 清理临时音频文件
            os.unlink(audio_path)

        # 如果指定了输出文件，保存到文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"文本已保存到: {output_file}")

        return text
