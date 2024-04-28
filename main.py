import asyncio
import datetime
import json
import os

import aiohttp
from load_dotenv import load_dotenv

import audio
from pipeline import Pipeline

load_dotenv()

BYTE_SIZE = (int)(audio.N_SAMPLES / 8)


async def post_data(data):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {os.getenv('WORKER_AUTH_TOKEN')}"}
        async with session.post(
            f"{os.getenv('GUARD_SERVER')}/worker/record", json=data, headers=headers
        ) as response:
            return await response.text()


async def process_audio_chunk(raw_bytes):
    import io

    from pydub import AudioSegment

    index = datetime.datetime.now().timestamp() * 1000  # unix timestamp

    # create audio
    audio_segment = AudioSegment.from_file(
        io.BytesIO(raw_bytes),
        format="raw",
        sample_width=2,
        frame_rate=audio.SAMPLE_RATE,
        channels=2,
    )

    path = f"chunks/chunk_{index}.mp3"
    audio_segment.export(path, format="mp3")
    text = audio.transcribe_audio(path, index)
    if text:
        if len(text) > 35:
            pipeline = Pipeline(os.getenv("REGION"))
            logs, events = pipeline.parse_incident(text)
            data = {"logs": logs, "events": events}
            asyncio.create_task(post_data(data))
    return


async def fetch_data(stream_url):  # main continuous stream
    chunks = b""
    total_bytes = 0
    timeout = aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(stream_url) as response:
            if response.status == 200:
                async for chunk in response.content.iter_any():
                    chunks += chunk
                    total_bytes += len(chunk)
                    if total_bytes >= BYTE_SIZE:
                        asyncio.create_task(process_audio_chunk(chunks[:BYTE_SIZE]))
                        chunks = chunk[BYTE_SIZE:]
                        total_bytes -= BYTE_SIZE
            else:
                print(
                    f"failed to fetch stream chunk: \
                        {response.status}, {response.content}"
                )


if __name__ == "__main__":
    if os.getenv("ENV") == "DEV":
        import uuid

        print("running DEV test...")

        index = uuid.uuid4()
        video = os.getenv("VIDEO", "chinks/test_chunks/emory-protests.mp3")
        text = audio.transcribe_audio(video, index)
        if text:
            print(f"transcribed: {text}\n")

            REGION = "Atlanta, Georgia"
            pipeline = Pipeline(REGION)
            logs, events = pipeline.parse_incident(text)
            data = {
                "logs": [log.to_json() for log in logs],
                "events": [event.to_json() for event in events],
            }
            print(data)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(post_data(data))
            print("done...")
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(fetch_data(os.getenv("STREAM_URL")))
