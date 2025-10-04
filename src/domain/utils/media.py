from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.fx.Resize import Resize
from typing import BinaryIO
from typing import Optional
import subprocess
import tempfile
import shlex

from aiogram import Bot
from aiogram.types import FSInputFile, InputFile


def process_video(videoIO: BinaryIO) -> Optional[InputFile]:

    temp_input = None
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(videoIO.read())
        temp_input = temp_file.name

    temp_output = None
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
        temp_output = temp_file.name

    if temp_input:
        clip = VideoFileClip(temp_input)
        clip = clip.subclipped(0, 3)
        clip_resized = clip.with_effects([Resize(height=512, width=512)])
        clip_an = clip_resized.without_audio()

        txt_clip = TextClip(
            font="Impact.ttf",
            text="HA HA HA \nСИТУАЦИЯ\n ХУЙ В ГОВНЕ",
            stroke_width=1,
            stroke_color="black",
            text_align="center",
            font_size=42,
            color='white'
        ).with_duration(3).with_position('bottom')

        final_video = CompositeVideoClip([clip_an, txt_clip])

        final_video.write_videofile(temp_output, codec="libvpx-vp9", fps=24)

    return FSInputFile(path=temp_output)

async def create_input_file(bot: Bot, id: str) -> Optional[InputFile]:
    file_info = await bot.get_file(id)
    assert file_info.file_path
    raw_file = await bot.download_file(file_info.file_path)
    assert raw_file
    return process_video(raw_file)

def from_bytes_to_bytes(
        input_bytes: bytes,
        action: str = "-f wav -acodec pcm_s16le -ac 1 -ar 44100")-> Optional[bytes]:
    command = f"ffmpeg -y -t 00:03:00 -i /dev/stdin -f nut {action} -"
    ffmpeg_cmd = subprocess.Popen(
        shlex.split(command),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        shell=False
    )
    b = b''
    # write bytes to processe's stdin and close the pipe to pass
    # data to piped process
    ffmpeg_cmd.stdin.write(input_bytes)
    ffmpeg_cmd.stdin.close()
    while True:
        output = ffmpeg_cmd.stdout.read()
        if len(output) > 0:
            b += output
        else:
            error_msg = ffmpeg_cmd.poll()
            if error_msg is not None:
                break
    return b