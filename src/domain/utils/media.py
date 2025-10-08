from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.fx.Resize import Resize
from src.domain.utils.consts import Consts
from typing import BinaryIO, Optional
from src.data.config import Prefs
import tempfile
import os

from aiogram import Bot
from aiogram.types import FSInputFile, InputFile, File

prefs = Prefs()

bot = Bot(token=prefs.bot_token)

def process_video(videoIO: BinaryIO, clip_text: Optional[str]) -> Optional[InputFile]:

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
            text=clip_text,
            stroke_width=1,
            stroke_color="black",
            text_align="center",
            font_size=42,
            color='white'
        ).with_duration(3).with_position('bottom')

        final_video = CompositeVideoClip([clip_an, txt_clip])

        final_video.write_videofile(temp_output, codec="libvpx-vp9", fps=24, bitrate="192K")

    return FSInputFile(path=temp_output)

async def make_sticker_webm_video(bot: Bot, id: str, clip_text: Optional[str]) -> Optional[InputFile]:
    file_info = await bot.get_file(id)
    assert file_info.file_path
    raw_file = await bot.download_file(file_info.file_path)
    assert raw_file
    return process_video(raw_file, clip_text)

async def save_file_by_tg_id(id:int) -> Optional[str]:
    try:
        os.chdir(Consts.PROJECTS_DIR)
        full_path = os.path.join(Consts.PROJECTS_DIR, f"{id}")
        with open(full_path, 'wb') as output_file_handler:
            tg_file = await bot.get_file(id)
            raw_file = await bot.download_file(tg_file.file_path)
            output_file_handler.write(raw_file.read())
        return full_path
    except Exception as e:
        print(f"Что-то пошло не так при сохранении: {e}")
        return None