import os
import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import yt_dlp
from typing import List, Tuple, Optional

# 可选导入 magic 库
try:
    import magic
    has_magic = True
except ImportError:
    has_magic = False


class VideoDownloader:
    def __init__(self, output_dir: str = None, debug: bool = False):
        """
        初始化视频下载器
        :param output_dir: 视频保存目录，默认为当前目录
        :param debug: 是否启用调试模式，保存页面内容
        """
        self.output_dir = output_dir or os.getcwd()
        self.debug = debug
        os.makedirs(self.output_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def save_debug_info(self, content: str, filename: str):
        """保存调试信息到文件"""
        if self.debug:
            debug_dir = os.path.join(self.output_dir, "debug")
            os.makedirs(debug_dir, exist_ok=True)
            filepath = os.path.join(debug_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"调试信息已保存到: {filepath}")

    def extract_video_urls(self, url: str) -> List[Tuple[str, str]]:
        """
        从网页中提取所有视频URL
        :param url: 网页URL
        :return: 视频URL列表，格式为 [(video_url, video_title), ...]
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 保存调试信息
            self.save_debug_info(response.text, "page_content.html")

            video_urls = []

            # 方法1: 查找 <video> 标签及其 source 子标签
            video_tags = soup.find_all('video')
            for idx, video in enumerate(video_tags):
                # 查找 <source> 子标签
                source_tags = video.find_all('source')
                if source_tags:
                    for src_idx, source in enumerate(source_tags):
                        src = source.get('src')
                        if src:
                            full_url = urljoin(url, src)
                            title = video.get('title', f'video_{idx + 1}_src_{src_idx + 1}')
                            video_urls.append((full_url, title))
                else:
                    # 直接在 video 标签上找 src
                    src = video.get('src')
                    if src:
                        full_url = urljoin(url, src)
                        title = video.get('title', f'video_{idx + 1}')
                        video_urls.append((full_url, title))

            # 方法2: 查找 <iframe> 标签（可能包含视频播放器）
            iframe_tags = soup.find_all('iframe')
            for idx, iframe in enumerate(iframe_tags):
                src = iframe.get('src')
                if src:
                    full_url = urljoin(url, src)
                    title = iframe.get('title', f'iframe_video_{idx + 1}')
                    video_urls.append((full_url, title))

            # 方法3: 查找包含视频链接的 <a> 标签
            video_extensions = ['.mp4', '.webm', '.m3u8', '.avi', '.mov', '.mkv', '.flv']
            a_tags = soup.find_all('a', href=True)
            for idx, a in enumerate(a_tags):
                href = a.get('href', '')
                if any(ext in href.lower() for ext in video_extensions):
                    full_url = urljoin(url, href)
                    title = a.get('title', a.get_text(strip=True) or f'link_video_{idx + 1}')
                    video_urls.append((full_url, title))

            # 方法4: 从JavaScript中提取视频URL
            script_tags = soup.find_all('script')
            for script in script_tags:
                script_content = script.string or ''
                # 查找常见的视频URL模式
                patterns = [
                    r'["\'](https?://[^"\']+\.mp4[^"\']*)["\']',
                    r'["\'](https?://[^"\']+\.webm[^"\']*)["\']',
                    r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']',
                    r'src\s*[:=]\s*["\'](https?://[^"\']+)["\']',
                    r'file\s*[:=]\s*["\'](https?://[^"\']+)["\']',
                    r'url\s*[:=]\s*["\'](https?://[^"\']+)["\']',
                    # 特定网站的视频模式
                    r'video\s*[:=]\s*["\']([^"\']+)["\']',
                    r'videoUrl\s*[:=]\s*["\']([^"\']+)["\']',
                    r'video_src\s*[:=]\s*["\']([^"\']+)["\']',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, script_content)
                    for match in matches:
                        if any(ext in match.lower() for ext in video_extensions) or 'video' in match.lower():
                            full_url = urljoin(url, match)
                            if full_url not in [v[0] for v in video_urls]:
                                video_urls.append((full_url, f'extracted_video_{len(video_urls) + 1}'))

            # 方法5: 查找 data-* 属性中的视频URL
            all_tags = soup.find_all(True)
            for idx, tag in enumerate(all_tags):
                for attr in tag.attrs:
                    if 'data-' in attr and 'video' in attr.lower() or any(ext in str(tag.attrs[attr]).lower() for ext in video_extensions):
                        value = tag.attrs[attr]
                        if any(ext in str(value).lower() for ext in video_extensions) or 'http' in str(value):
                            # 尝试解析可能包含的JSON字符串
                            try:
                                import json
                                # 替换可能的转义字符
                                json_str = str(value).replace(r'\\', '\\')
                                # 尝试解析JSON
                                data = json.loads(json_str)
                                # 在解析后的JSON中查找视频URL
                                if isinstance(data, dict) and 'video' in data and isinstance(data['video'], dict) and 'url' in data['video']:
                                    video_url = data['video']['url']
                                    # 处理转义的斜杠
                                    video_url = video_url.replace(r'\\', '/')
                                    full_url = urljoin(url, video_url)
                                    if full_url not in [v[0] for v in video_urls]:
                                        video_urls.append((full_url, f'data_video_{idx + 1}'))
                                elif isinstance(data, dict) and 'url' in data:
                                    full_url = urljoin(url, data['url'])
                                    if full_url not in [v[0] for v in video_urls]:
                                        video_urls.append((full_url, f'data_video_{idx + 1}'))
                                else:
                                    # 直接处理字符串值
                                    full_url = urljoin(url, str(value))
                                    if full_url not in [v[0] for v in video_urls]:
                                        video_urls.append((full_url, f'data_video_{idx + 1}'))
                            except Exception as e:
                                # 如果不是有效的JSON或解析失败，直接使用原始值
                                full_url = urljoin(url, str(value))
                                if full_url not in [v[0] for v in video_urls]:
                                    video_urls.append((full_url, f'data_video_{idx + 1}'))

            return video_urls

        except Exception as e:
            print(f"提取视频URL失败: {str(e)}")
            return []

    def sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，移除非法字符
        """
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        filename = filename.strip()
        # 限制文件名长度
        if len(filename) > 100:
            filename = filename[:100]
        return filename or 'video'

    def is_video_content(self, content_type: str, filepath: str = None) -> bool:
        """
        判断是否为视频内容
        """
        if content_type and any(subtype in content_type.lower() for subtype in ['video/', 'application/octet-stream']):
            if filepath and os.path.exists(filepath):
                try:
                    if has_magic:
                        # 使用 magic 库判断文件类型
                        mime = magic.Magic(mime=True)
                        file_mime = mime.from_file(filepath)
                        return file_mime.startswith('video/') or file_mime == 'application/octet-stream'
                    else:
                        # 如果没有 magic 库，至少需要 1MB 大小的文件才认为是视频
                        file_size = os.path.getsize(filepath)
                        if file_size < 1024 * 1024:  # 小于 1MB 的视频可能性不大
                            return False
                except Exception:
                    pass

            return True
        return False

    def download_with_yt_dlp(self, url: str, title: str = None) -> Optional[str]:
        """
        使用 yt-dlp 下载视频（支持更多网站和格式）
        :param url: 视频URL
        :param title: 视频标题
        :return: 下载的文件路径，失败返回None
        """
        try:
            safe_title = self.sanitize_filename(title or 'video')
            output_path = os.path.join(self.output_dir, safe_title)

            ydl_opts = {
                'outtmpl': output_path + '.%(ext)s',
                'quiet': False,
                'no_warnings': False,
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
                'continuedl': True,
                'noprogress': False,
                # 优化 HLS 下载
                'hls_prefer_native': True,
                'hls_use_mpegts': False,
                'retries': 10,
                'fragment_retries': 10,
                'skip_unavailable_fragments': True,
                'buffer_size': 1024*1024*64,
                'http_chunk_size': 1024*1024*10,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    if 'requested_downloads' in info:
                        for download in info['requested_downloads']:
                            if 'filepath' in download:
                                return download['filepath']
                    video_id = info.get('id', '')
                    ext = info.get('ext', 'mp4')
                    return os.path.join(self.output_dir, f"{safe_title}.{ext}")

        except Exception as e:
            print(f"yt-dlp 下载失败: {str(e)}")
            return None

    def download_direct(self, url: str, title: str = None) -> Optional[str]:
        """
        直接下载视频文件（适用于直接的视频链接）
        :param url: 视频URL
        :param title: 视频标题
        :return: 下载的文件路径，失败返回None
        """
        try:
            safe_title = self.sanitize_filename(title or 'video')

            parsed = urlparse(url)
            path = parsed.path
            ext = os.path.splitext(path)[1]
            if not ext or len(ext) > 5:
                ext = '.mp4'

            output_path = os.path.join(self.output_dir, safe_title + ext)

            print(f"正在下载: {title or url}")
            print(f"保存到: {output_path}")

            with self.session.get(url, stream=True, timeout=60) as response:
                response.raise_for_status()

                # 检查 Content-Type 是否为视频类型
                content_type = response.headers.get('content-type', '')
                if not any(subtype in content_type.lower() for subtype in ['video/', 'application/octet-stream']):
                    print(f"警告: 响应内容类型不是视频类型 ({content_type})，可能下载的是HTML页面")
                    print("取消下载...")
                    return None

                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0

                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                print(f"\r下载进度: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='')

            print(f"\n下载完成: {output_path}")

            # 验证下载的文件是否是视频
            if not self.is_video_content(content_type, output_path):
                print("错误: 下载的文件不是有效的视频文件")
                try:
                    os.remove(output_path)
                except:
                    pass
                return None

            return output_path

        except Exception as e:
            print(f"直接下载失败: {str(e)}")
            return None

    def decode_url(self, url: str) -> str:
        """解码 URL"""
        import urllib.parse
        try:
            return urllib.parse.unquote(url)
        except Exception:
            return url

    def cleanup_url(self, url_str: str) -> str:
        """清理 URL，去除不需要的部分"""
        import urllib.parse
        try:
            # 先解码 URL
            decoded = urllib.parse.unquote(url_str)

            # 现在检查解码后的字符串是否包含 JSON
            if '{' in decoded or '}' in decoded:
                # 情况1: URL 包含 JSON 字符串（如测试案例）
                # 找到 JSON 开始位置 '{'
                json_start = decoded.find('{')
                if json_start != -1:
                    json_end = decoded.rfind('}') + 1
                    json_str = decoded[json_start:json_end]

                    try:
                        import json
                        data = json.loads(json_str)
                        if isinstance(data, dict) and 'video' in data and isinstance(data['video'], dict) and 'url' in data['video']:
                            video_url = data['video']['url'].replace(r'\\', '/')
                            return video_url
                    except Exception as e:
                        print(f"解析 JSON 时出错: {e}")

                # 情况2: 尝试直接在字符串中查找 HTTP(S) 协议的 URL
                import re
                url_pattern = r'(https?://[^\s"\']+)'
                matches = re.findall(url_pattern, decoded)
                if matches:
                    return matches[0]

        except Exception as e:
            print(f"解码 URL 时出错: {e}")

        return url_str

    def download_video(self, url: str, title: str = None) -> Optional[str]:
        """
        下载视频（自动选择最佳方法）
        :param url: 视频URL
        :param title: 视频标题
        :return: 下载的文件路径，失败返回None
        """
        # 清理和验证 URL
        clean_url = self.decode_url(self.cleanup_url(url))
        if clean_url != url:
            print(f"自动解析到真实视频URL: {clean_url}")

        # 首先使用 yt-dlp 下载
        result = self.download_with_yt_dlp(clean_url, title)
        if result and os.path.exists(result):
            return result

        print("yt-dlp 无法下载，尝试直接下载...")
        return self.download_direct(clean_url, title)

    def process_url(self, url: str) -> List[str]:
        """
        处理网页URL，提取并下载所有视频
        :param url: 网页URL
        :return: 下载的视频文件路径列表
        """
        print(f"正在分析网页: {url}")
        video_urls = self.extract_video_urls(url)

        if not video_urls:
            print("未在网页中找到视频URL")
            # 不要尝试直接下载网页URL，因为会下载HTML文件
            return []

        print(f"找到 {len(video_urls)} 个视频:")
        for idx, (video_url, title) in enumerate(video_urls, 1):
            print(f"  {idx}. {title} - {video_url}")

        downloaded_files = []
        for idx, (video_url, title) in enumerate(video_urls, 1):
            print(f"\n{'='*60}")
            print(f"正在下载视频 {idx}/{len(video_urls)}: {title}")
            print(f"{'='*60}")

            result = self.download_video(video_url, title)
            if result:
                downloaded_files.append(result)
                print(f"成功下载: {result}")
            else:
                print(f"下载失败: {title}")

        return downloaded_files
