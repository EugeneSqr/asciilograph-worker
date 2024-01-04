import sys
import os
import signal
import asyncio
from types import FrameType

from ascii_magic import AsciiArt

from settings import get_settings
from queues import get_channel, image_processing_messages, return_processed_image
from fileserver import download_image

def _signal_handler(signum: int, _: FrameType | None) -> None:
    print(f"Signal received {signal.Signals(signum).name} ({signum})")
    print("Restarting the worker process")
    asyncio.get_running_loop().stop()
    os.execl(sys.executable, sys.executable, * sys.argv)
    print("Restarting done")

signal.signal(signal.SIGHUP, _signal_handler)

async def start_worker(worker_id: int) -> None:
    print(f"worker {worker_id} has started")
    future = asyncio.get_running_loop().create_future()
    async with get_channel() as channel:
        async for message in image_processing_messages(channel):
            async with message.process(requeue=False):
                ascii_art = AsciiArt.from_pillow_image(await download_image(message.body.decode()))
                await return_processed_image(
                    channel,
                    ascii_art.to_ascii(),
                    message.correlation_id,
                    message.reply_to,
                )
    await future
    print(f"worker {worker_id} has finished")

async def main() -> None:
    print("starting workers")
    async with asyncio.TaskGroup() as worker_tasks:
        for i in range(get_settings().workers_count):
            worker_tasks.create_task(start_worker(i))
    print("all workers done")

if __name__ == "__main__":
    asyncio.run(main())
