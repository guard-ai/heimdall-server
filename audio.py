import whisper

CHUNK_LENGTH = 30
SAMPLE_RATE = 16000
N_SAMPLES = CHUNK_LENGTH * SAMPLE_RATE
model = whisper.load_model("medium.en")


def transcribe_audio(path, index):
    result = model.transcribe(path)
    text = str(result["text"])

    with open(f'records/record_{index}.txt', 'w') as file:
        if text:
            text = text.strip()
            file.write(text)
            return text

    return None
