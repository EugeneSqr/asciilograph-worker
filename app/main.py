import sys
import os
import signal
import asyncio
import logging
from types import FrameType

from ascii_magic import AsciiArt

from settings import get_settings
from queues import get_channel, image_processing_messages, return_processed_image
from fileserver import download_image
from logger import configure_logging

def _signal_handler(signum: int, _: FrameType | None) -> None:
    logging.info(f"Signal received {signal.Signals(signum).name} ({signum})")
    logging.info("Restarting the worker process")
    asyncio.get_running_loop().stop()
    os.execl(sys.executable, sys.executable, * sys.argv)
    logging.info("Restarting done")

signal.signal(signal.SIGHUP, _signal_handler)

async def start_worker(worker_id: int, worker_tasks: asyncio.TaskGroup) -> None:
    logging.info(f"worker {worker_id} has started")
    try:
        async with get_channel() as channel:
            async for message in image_processing_messages(channel):
                async with message.process(requeue=False):
                    ascii_art = AsciiArt.from_pillow_image(
                        await download_image(message.body.decode()))
                    await return_processed_image(
                        channel,
                        ascii_art.to_ascii(),
                        message.correlation_id,
                        message.reply_to,
                    )
    except Exception as e:
        logging.error(f"something went wrong, restarting worker {worker_id}: {e}")
        worker_tasks.create_task(start_worker(worker_id, worker_tasks))
    logging.info(f"worker {worker_id} has finished")

async def main() -> None:
    logging.info("starting workers")
    async with asyncio.TaskGroup() as worker_tasks:
        for i in range(get_settings().workers_count):
            worker_tasks.create_task(start_worker(i, worker_tasks))
    logging.info("all workers done")

if __name__ == "__main__":
    configure_logging()
    asyncio.run(main())
