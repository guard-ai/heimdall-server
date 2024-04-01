from openai_client import OpenAIClient
from locations import LocationResolver


class Pipeline(object):
    def __init__(self, region):
        self.region = region
        self.openai_client = OpenAIClient(self.region)
        self.location = LocationResolver()

    def parse_incident(self, text):
        log, events = self.openai_client.run(text)

        location_cache = {}

        for event in events:
            if event.location in location_cache:
                lat = location_cache[event.location].coords[0]
                lon = location_cache[event.location].coords[1]
                event.location = f"{lat},{lon}"
            else:
                locations = self.location.resolve(event.location, self.region)
                lat = locations[0].coords[0]
                lon = locations[0].coords[1]
                event.location = f"{lat},{lon}"

        return log, events
