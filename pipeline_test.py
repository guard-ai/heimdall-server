import uuid
from dotenv import load_dotenv

import audio
from pipeline import Pipeline

load_dotenv()

# The following is a transcript from the following
# dispatcher call: https://www.youtube.com/watch?v=E85VckohGcs
# The above transcript is from the Aurora, Colorado shooting at
# Century 16 theaters on July 20th, 2012.

TRANSCRIPT = """
three-sixteen okay units stand by for charge
3-15 and 3-40 shooting at Century theaters
14300 East Alameda Avenue they're saying
somebody's shooting in the auditorium
eNOS responding to the shootings which
to remain on channel 2 channel specs
normal.

3-15 and 3-40 there is at least
one person has been shot but they're
saying there's hundreds of people just
running around.
"""

REGION = "Aurora, Colorado"


def test_end_to_end():
    index = uuid.uuid4()
    text = audio.transcribe_audio(
        "chunks/test_chunks/aurora-colorado-shooting.mp3", index)
    if text:
        print(f"transcribed: {text}\n")

        pipeline = Pipeline(REGION)
        logs, events = pipeline.parse_incident(text)

        for log in logs:
            print(f"{log}\n")
        for event in events:
            print(f"{event}\n")


if __name__ == "__main__":
    test_end_to_end()
