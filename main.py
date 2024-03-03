from fastapi import BackgroundTasks, FastAPI, Request
import numpy as np
from audio_to_text_stream import AudioToText
import uvicorn
import asyncio

app = FastAPI()

at = AudioToText()

async def process_data(data):
    print("start")
    data = np.array(data, dtype=np.float32)
    text = at.decode(data)
    print(text)

@app.post("/audio_to_text")
async def process_and_post(request: Request):
    data = await request.json()
    print(len(data))
    asyncio.create_task(process_data(data))

    return {"message": "Request added to the queue"}

def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)

if __name__ == "__main__":
    main()