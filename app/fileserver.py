from io import BytesIO

import aioftp
from PIL import Image

from settings import get_settings

async def download_image(image_key: str) -> Image.Image:
    settings = get_settings()
    async with aioftp.Client.context(settings.fileserver_address,
                                     user=settings.fileserver_user,
                                     password=settings.fileserver_password) as ftp_client:
        buffer = BytesIO()
        async with ftp_client.download_stream(image_key) as download_stream:
            async for chunk in download_stream.iter_by_block():
                buffer.write(chunk)
        return Image.open(buffer)
