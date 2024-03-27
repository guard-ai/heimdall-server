from dataclasses import dataclass
from openai_client import OpenAIClient
from locations import LocationResolver
import json
import uuid
from datetime import datetime, date


@dataclass
class Log:
    id: uuid.UUID
    region: str
    utterance: str
    created_at: date


@dataclass
class Event:
    id: uuid.UUID
    level: int
    location: str
    category: str
    log_id: uuid.UUID
    created_at: date


def parse(res):
    res = res.split('|')
    res = [r.replace(' ', '') for _, r in enumerate(res)]
    res = [r.split(':')[1]
           for _, r in enumerate(res)]  # type, loc, lvl ~ 0, 1, 2
    res[2] = int(res[2])
    return res


class Pipeline(object):
    def __init__(self, region, text):
        self.openai_client = OpenAIClient(self.region)
        self.location = LocationResolver()
        self.region = region
        self.text = text

    def unpack_incident(self):
        if self.openai_client.is_incident(self.text) == "YES":
            return self.openai_client.analyze_incident(self.text)
        return None

    def pack_json(self, incident):
        r = parse(incident)
        cur_date = datetime.now().date()

        self.location = r[1]  # the query
        parsed_location = self.openai_client.for_google(
            self.region, self.location)
        locations = self.location.resolve(parsed_location, self.region)

        event_instance = Event(
            id=uuid.uuid4(),
            level=r[2],
            location=f"{locations[0][0]},{locations[0][1]}",
            category=r[0],
            log_id=uuid.uuid4(),
            created_at=cur_date,
        )

        log_instance = Log(
            id=uuid.uuid4(),
            region=self.region,
            utterance=self.text,
            created_at=cur_date
        )

        data = {
            "events": event_instance,
            "logs": log_instance
        }

        return json.dumps(data, default=str, indent=4)
