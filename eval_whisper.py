import asyncio
import aiohttp
import audio
import datetime

BYTE_SIZE = (int)(audio.N_SAMPLES/8)
SOURCES = []

async def process_audio_chunk(raw_bytes):
    from pydub import AudioSegment
    import io

    index = datetime.datetime.now().timestamp() * 1000

    # create audio
    audio_segment = AudioSegment.from_file(
        io.BytesIO(raw_bytes), format='raw',
        sample_width=2, frame_rate=audio.SAMPLE_RATE, channels=2
    )

    path = f'whisper_eval/chunk_{index}.mp3'
    audio_segment.export(path, format='mp3')
    text = audio.transcribe_audio(path, index)

    with open(f"whisper_eval/text/text_{index}.txt", "w") as f:
        if text:
            f.write(text)
        else:
            f.write("text: None")

async def fetch_data(stream_url, num):
    print(f"Starting with url number: {num}:")
    end = 0
    chunks = b''
    total_bytes = 0
    timeout = aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(stream_url) as response:
            if response.status == 200:
                async for chunk in response.content.iter_any():
                    chunks += chunk
                    total_bytes += len(chunk)
                    if end == 5:
                        return
                    if total_bytes >= BYTE_SIZE:
                        asyncio.create_task(process_audio_chunk(
                            chunks[:BYTE_SIZE]))
                        print(f"Audio Task for {num} started!")
                        chunks = chunk[BYTE_SIZE:]
                        total_bytes -= BYTE_SIZE
                        end += 1
            else:
                print(f"failed to fetch stream chunk: \
                        {response.status}, {response.content}")


if __name__ == "__main__":
    # read
    with open('top50.txt', 'r') as file:
        file_contents = file.read()
        lines = file_contents.splitlines()

        for line in lines:
            SOURCES.append(line)

    loop = asyncio.get_event_loop()
    for num, i in enumerate(SOURCES):
        print(i)
        loop.run_until_complete(fetch_data(i, num))
