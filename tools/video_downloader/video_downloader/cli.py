import click
import os
from .core import VideoDownloader


@click.command()
@click.argument('url')
@click.option('-o', '--output-dir', default='.', help='视频保存目录，默认为当前目录')
@click.option('-d', '--debug', is_flag=True, help='启用调试模式，保存页面内容')
@click.version_option(version='0.1.0')
def main(url, output_dir, debug):
    """
    通用视频下载工具

    输入包含视频的网页URL，自动提取并下载所有可用的视频。
    支持多种视频来源和格式。

    示例:
        video-downloader https://example.com/video-page
        video-downloader https://example.com/video-page -o ./videos
    """
    try:
        # 确保输出目录存在
        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)

        click.echo(f"视频下载器启动")
        click.echo(f"目标URL: {url}")
        click.echo(f"输出目录: {output_dir}")
        click.echo(f"调试模式: {'开启' if debug else '关闭'}")
        click.echo("-" * 60)

        downloader = VideoDownloader(output_dir=output_dir, debug=debug)
        downloaded_files = downloader.process_url(url)

        click.echo("\n" + "=" * 60)
        if downloaded_files:
            click.echo(f"下载完成！共下载 {len(downloaded_files)} 个视频:")
            for idx, filepath in enumerate(downloaded_files, 1):
                if filepath:
                    click.echo(f"  {idx}. {filepath}")
        else:
            click.echo("未成功下载任何视频")
        click.echo("=" * 60 + "\n")

    except Exception as e:
        click.echo(f"处理失败: {str(e)}", err=True)
        import traceback
        click.echo(traceback.format_exc(), err=True)
        raise click.Abort()


if __name__ == '__main__':
    main()
