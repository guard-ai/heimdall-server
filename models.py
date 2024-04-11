from json import JSONEncoder


class Log(JSONEncoder):
    def __init__(self, id, region, utterance):
        self.id = id
        self.region = region
        self.utterance = utterance

    def to_json(self):
        return {
            "id": f"{self.id}",
            "region": f"{self.region}",
            "utterance": f"{self.utterance}",
        }

    def __repr__(self):
        return f"id: {self.id}, region: {self.region}, utterance: {self.utterance}"

    def __str__(self):
        return f"id: {self.id}, region: {self.region}, utterance: {self.utterance}"


class Event(JSONEncoder):
    def __init__(self, id, level, location, category, log_id, description):
        self.id = id
        self.level = level
        self.location = location
        self.category = category
        self.log_id = log_id
        self.description = description

    def to_json(self):
        return {
            "id": f"{self.id}",
            "level": f"{self.level}",
            "location": f"{self.location}",
            "category": f"{self.category}",
            "log_id": f"{self.log_id}",
            "description": f"{self.description}",
        }

    def __repr__(self):
        return f"id: {self.id}, level: {self.level}, location: {self.location}, category: {self.category}, log_id: {self.log_id}, description: {self.description}"

    def __str__(self):
        return f"id: {self.id}, level: {self.level}, location: {self.location}, category: {self.category}, log_id: {self.log_id}, description: {self.description}"
