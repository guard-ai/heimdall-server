import json
import os
import uuid

import openai

from models import Event, Log


def record_incident(log_id, location, category, confirmation, level, description):
    return Event(
        id=uuid.uuid4(),
        level=f"{confirmation.strip().upper()}_{level.strip().upper()}",
        location=location.strip(),
        category=f"{category.strip()}",
        log_id=log_id,
        description=description,
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
            tools=[
                {
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
                                        location of the incident",
                                },
                                "category": {
                                    "type": "string",
                                    "description": "category of incident:\
                                        name or nature of the crime such as, \
                                        fire, traffic accident, medical, \
                                        hazards, robbery, etc.",
                                },
                                "confirmation": {
                                    "type": "string",
                                    "description": "'CONFIRMED' if the incident \
                                        has been confirmed by civilians, \
                                        units or the dispatcher. 'REPORTED' \
                                        if an incident is suspected but \
                                        requires further investigation by \
                                        authorities",
                                },
                                "level": {
                                    "type": "string",
                                    "description": "'THREAT' if the incident \
                                        poses an immediate risk on human life \
                                        and civilians should seek immediate \
                                        shelter. 'INFO' if the incident \
                                        poses some immediate risk to \
                                        civilians, and they should be aware.",
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Provide a short \
                                    description of the event that only \
                                    includes the relevant features needed \
                                    to inform the user.",
                                },
                            },
                            "required": [
                                "location",
                                "category",
                                "confirmation",
                                "level",
                            ],
                        },
                    },
                }
            ],
            tool_choice="auto",
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
                    description=function_args.get("description"),
                )

                events.append(event)

        return logs, events
