import whisper
model = whisper.load_model("base")

'''
Input: Audio Chunk of size 48000 (float 32)
Output: Text (string)
'''

class AudioToText(): 
    def decode(self, audio):
        mel = whisper.log_mel_spectrogram(audio).to(model.device)

        # detect the spoken language
        _, probs = model.detect_language(mel)
        print(f"Detected language: {max(probs, key=probs.get)}")

        # decode the audio
        options = whisper.DecodingOptions()
        result = whisper.decode(model, mel, options)
        return result.text