import asyncio
import aiohttp
import datetime
from load_dotenv import load_dotenv
import os
import whisper

from pipeline import Pipeline

load_dotenv()

# Constants for Whisper AI
model = whisper.load_model("base")
SAMPLE_RATE = 16000
CHUNK_LENGTH = 30
N_SAMPLES = CHUNK_LENGTH * SAMPLE_RATE
BYTE_SIZE = (int)(N_SAMPLES/8)


def decode_audio(audio):
    global model
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    _, probs = model.detect_language(mel)
    # detect the spoken language
    print(f"Detected language: {max(probs, key=probs.get)}")

    # decode the audio
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)
    if type(result) is list:
        return " ".join([r.text for r in result])
    elif type(result) is whisper.DecodingResult:
        return result.text

    return None


async def post_data(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.text()


async def process_audio_chunk(raw_bytes):
    from pydub import AudioSegment
    import io

    # unix timestamp
    index = datetime.datetime.now().timestamp() * 1000

    # create audio
    audio_segment = AudioSegment.from_file(
        io.BytesIO(raw_bytes), format='raw',
        sample_width=2, frame_rate=SAMPLE_RATE, channels=2
    )

    audio_segment.export(f'chunks/chunk_{index}.mp3', format='mp3')

    audio = whisper.load_audio(f'chunks/chunk_{index}.mp3')
    audio = whisper.pad_or_trim(audio, N_SAMPLES)

    # create textfile and text
    text = decode_audio(audio)
    with open(f'records/record_{index}.txt', 'w') as file:
        if text:
            print(f"translated text from streamed chunk: {text}")
            file.write(text)

    # clean up mp3 file that is no longer used
    os.remove(f'chunks/chunk_{index}.mp3')

    pipeline = Pipeline(os.getenv("REGION"))
    logs, events = pipeline.parse_incident(text)
    data = {"logs": logs, "events": events}
    asyncio.create_task(post_data(os.getenv("GUARD_SERVER"), data))
    return


async def fetch_data(stream_url):  # main continuous stream
    chunks = b''
    total_bytes = 0
    timeout = aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(stream_url) as response:
            if response.status == 200:
                async for chunk in response.content.iter_any():
                    chunks += chunk
                    total_bytes += len(chunk)
                    if total_bytes >= BYTE_SIZE:
                        asyncio.create_task(process_audio_chunk(
                            chunks[:BYTE_SIZE]))
                        chunks = chunk[BYTE_SIZE:]
                        total_bytes -= BYTE_SIZE
            else:
                print(f"failed to fetch stream chunk: \
                        {response.status}, {response.content}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_data(os.getenv("STREAM_URL")))
