from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from src.models.custom_sticker_model import CustomStickerModel
from moviepy.video.fx.Resize import Resize
from src.domain.utils.consts import Consts
from typing import BinaryIO, Optional
from src.data.config import Prefs
import moviepy.video.fx as vfx
from typing import List
import tempfile
import os

from aiogram import Bot
from aiogram.types import FSInputFile, InputFile, BufferedInputFile

prefs = Prefs()

bot = Bot(token=prefs.bot_token)

def process_media(videoIO: BinaryIO, clip_text: Optional[str]) -> Optional[List[str]]:
    try:
        temp_input = None
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            temp_file.write(videoIO.read())
            temp_input = temp_file.name

        temp_sticker = None
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            temp_sticker = temp_file.name

        temp_media = None
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            temp_media = temp_file.name

        if temp_input:
            clip = VideoFileClip(temp_input)
            clip = clip.with_effects([vfx.Resize(width=512)])

            print(f"input file meta: w:{clip.w}, h:{clip.h}, cx:{clip.w / 2}, cy:{clip.h / 2}")
            
            crop = vfx.Crop(x_center=clip.w / 2, y_center=clip.h / 2, width=512, height=512)
            clip = crop.apply(clip)
        
            clip_an = clip.without_audio()
            crop_an = clip_an.subclipped(0, 3)

            txt_clip = TextClip(
                font="Impact.ttf",
                text=clip_text,
                stroke_width=1,
                stroke_color="black",
                text_align="center",
                font_size=42,
                color='white'
            ).with_duration(3).with_position('bottom')

            print(f"output file meta: w:{crop_an.w}, h:{crop_an.h}")

            final_sticker = CompositeVideoClip([crop_an, txt_clip])
            final_media = CompositeVideoClip([clip, txt_clip])

            final_sticker.write_videofile(temp_sticker, codec="libvpx-vp9", fps=24, bitrate="192K")
            final_media.write_videofile(temp_media, codec="libvpx-vp9", fps=24, bitrate="192K")
            
            return [temp_sticker, temp_media]
    except Exception as e:
        print(f"convert error: {e}")
        return None

async def make_sticker_webm_video(bot: Bot, id: str, clip_text: Optional[str]) -> Optional[InputFile]:
    file_info = await bot.get_file(id)
    assert file_info.file_path
    raw_file = await bot.download_file(file_info.file_path)
    assert raw_file
    return process_media(raw_file, clip_text)

def get_media_by_custom_sticker(custom_sticker: CustomStickerModel) -> Optional[InputFile]:
    try:
        with open(custom_sticker.media_path, "rb") as output_file_handler:
            return BufferedInputFile(output_file_handler.read(), custom_sticker.sticker_id)
    except Exception as e:
        print("can't open file by path: {e}")

def save_file(source:bytes, file_name: str) -> Optional[str]:
    try:
        os.chdir(Consts.PROJECTS_DIR)
        full_path = os.path.join(Consts.PROJECTS_DIR, f"{file_name}")
        with open(full_path, 'wb') as output_file_handler:
            output_file_handler.write(source)
        return full_path
    except Exception as e:
        print(f"Что-то пошло не так при сохранении: {e}")
        return None

def delete_file(file_path: str) -> bool:
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"file deleted: {file_path}")
        return True
    else:
        print(f"file not exist: {file_path}")
        return False