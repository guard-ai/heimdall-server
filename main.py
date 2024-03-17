from fastapi import BackgroundTasks, FastAPI, Request
import numpy as np
from audio_to_text_stream import AudioToText
from response_manager import Organizer
import uvicorn
import asyncio
import aiohttp
import whisper

app = FastAPI()
at = AudioToText()

# Constants for Whisper AI
model = whisper.load_model("base")
SAMPLE_RATE = 16000
CHUNK_LENGTH = 30
N_SAMPLES = CHUNK_LENGTH * SAMPLE_RATE
BYTE_SIZE = (int)(N_SAMPLES/8)

# url = 'https://broadcastify.cdnstream1.com/41983'
url = 'https://broadcastify.cdnstream1.com/32602'
i = 0

async def w_audio(raw_bytes):
    global i
    from pydub import AudioSegment
    import io

    # create audio
    audio_segment = AudioSegment.from_file(
        io.BytesIO(raw_bytes), format='raw',
        sample_width=2, frame_rate=SAMPLE_RATE, channels=2
    )
    i += 1
    audio_segment.export(f'tests/test{i}.mp3', format='mp3')
    
    audio = whisper.load_audio(f'tests/test{i}.mp3')
    audio = whisper.pad_or_trim(audio, N_SAMPLES)

    # create textfile and text
    print(audio, audio.shape)
    text = at.decode(audio)
    print(text)
    with open(f'records/record{i}.txt', 'w') as file:
        file.write(text)

    # gpt verification
    

async def fetch_data(url): # main continuous stream
    global i
    print(f'Fetching Data {i}')
    chunks = b''
    total_bytes = 0  
    timeout = aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            if response.status == 200:
                async for chunk in response.content.iter_any():
                    chunks += chunk
                    total_bytes += len(chunk)
                    if total_bytes >= BYTE_SIZE:  
                        asyncio.create_task(w_audio(chunks[:BYTE_SIZE]))
                        chunks = chunk[BYTE_SIZE:]
                        total_bytes -= BYTE_SIZE
            else:
                print('Failed to fetch data:', response.status)

@app.get("/stream")
async def stream_data():
    await fetch_data(url)

def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()