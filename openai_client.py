import datetime
import os
import uuid
import openai
import json

from models import Event, Log


def record_incident(log_id, location, category, confirmation, level):
    return Event(
        id=uuid.uuid4(),
        level=level,
        location=location,
        category=f"{confirmation.strip()}: {category.strip()}",
        log_id=log_id,
        created_at=datetime.datetime.now().date(),
    )


class OpenAIClient(object):
    def __init__(self, region):
        self.region = region
        openai.api_key = os.getenv("OPENAI_KEY")

    def run(self, transcribed_text):
        message = f"""
        Listen to the following radio communication from {self.region}.
        The radio communication was transcribed and may have typos, code words,
        or incoherent text. Analyze the text and fill in typos, code words, or
        incoherent text to the best of your ability and record any and all
        incidents if present: {transcribed_text}.
        """
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[{"role": "user", "content": message}],
            tools=[{
                "type": "function",
                "function": {
                    "name": "record_incident",
                    "description": "Record an incident from a chunk of text \
                            transcribed from first responder radio",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "a search query to provide \
                                        Google maps that identifies the \
                                        location of the incident"
                            },
                            "category": {
                                "type": "string",
                                "description": "category of incident:\
                                        name or nature of the crime such as, \
                                        fire, traffic accident, medical, \
                                        hazards, robbery, etc."
                            },
                            "confirmation": {
                                "type": "string",
                                "description": "'Confirmed' if the incident \
                                        has been confirmed by civilians, \
                                        units or the dispatcher. 'Reported' \
                                        if an incident is suspected but \
                                        requires further investigation by \
                                        authorities"
                            },
                            "level": {
                                "type": "string",
                                "description": "'HIGH' if the incident poses \
                                        an immediate risk on human life and \
                                        civilians should seek immediate \
                                        shelter. 'MEDIUM' if the incident \
                                        poses some immediate risk to \
                                        civilians, and they should be aware. \
                                        'LOW' if the incident does not pose \
                                        an immediate risk to civilians but \
                                        they should be aware."
                            },
                        },
                        "required": ["location", "category", "confirmation",
                                     "level"]
                    }
                }
            }],
            tool_choice="auto"
        )
        response = completion.choices[0].message
        tool_calls = response.tool_calls

        events = []
        logs = []

        if tool_calls:
            available_functions = {
                "record_incident": record_incident,
            }

            log = Log(
                id=uuid.uuid4(),
                region=self.region,
                utterance=transcribed_text,
                created_at=datetime.datetime.now().date()
            )

            logs.append(log)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                event = function_to_call(
                    log_id=log.id,
                    location=function_args.get("location"),
                    category=function_args.get("category"),
                    confirmation=function_args.get("confirmation"),
                    level=function_args.get("level"),
                )

                events.append(event)

        return logs, events
