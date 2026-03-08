import click
from .core import BilibiliProcessor

@click.command()
@click.argument('url')
@click.option('-o', '--output', help='输出文本文件路径，默认直接打印到控制台')
@click.option('-a', '--audio-dir', help='音频文件保存目录，默认使用临时目录并自动删除')
@click.option('-m', '--model', default='base', help='Whisper模型大小: tiny, base, small, medium, large (默认: base)')
@click.version_option(version='0.1.0')
def main(url, output, audio_dir, model):
    """
    B站视频文本提取工具

    输入B站视频URL，自动提取字幕或通过语音识别生成文本
    """
    try:
        processor = BilibiliProcessor(whisper_model=model)
        text = processor.process_video(url, output, audio_output_dir=audio_dir)

        if not output:
            click.echo("\n" + "="*50)
            click.echo("提取的文本内容：")
            click.echo("="*50)
            click.echo(text)
            click.echo("="*50 + "\n")

        click.echo("处理完成！")

    except Exception as e:
        click.echo(f"处理失败: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    main()
