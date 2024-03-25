from dataclasses import dataclass
from gpt_and_struct import open_AI
import json
import uuid
from datetime import datetime, date

@dataclass
class logStruct:
    Id: uuid
    Region: str
    Utterance: str
    CreatedAt: date

@dataclass
class eventStruct:
    Id: uuid
    Level: int
    Location: str 
    Category: str
    LogId: uuid 
    CreatedAt: date

def text_to_tuple(res):
    res = res.split('|')
    res = [r.replace(' ', '') for i, r in enumerate(res)]
    res = [r.split(':')[1] for i, r in enumerate(res)] #type, loc, lvl ~ 0, 1, 2
    res[2] = int(res[2])
    return res
    
class Organizer(object):
    def __init__(self, reg , text):
        self.instance = open_AI(self.reg)
        self.reg = reg
        self.text = text
        self.location = None
        self.res = None

    def aggregate_gpt_call(self):
        if self.instance.is_incident(self.text)=="YES":
            self.res = self.instance.analyze_incident(self.text)

    def re_structure(self):
        r = text_to_tuple(self.res)
        cur_date = datetime.now().date()
        
        ### CAN ADD LOCATION LOGIC HERE
        self.location = r[1] #the query
        self.location = self.instance.for_google(self.reg, self.location) #added a gpt call for you to play around

        self.event_instance = eventStruct(
            Id = uuid.uuid4(),
            Level =r[2],
            Location =r[1],
            Category =r[0],
            LogId = uuid.uuid4(),
            CreatedAt= cur_date,
            )
        
        self.log_instance = logStruct(
            Id = uuid.uuid4(),
            Region = self.reg,
            Utterance = self.text,
            CreatedAt = cur_date
            )
        
        data = {
            "Event": self.event_instance,
            "Log": self.log_instance
            }
        self.json_data = json.dumps(data, default=str, indent=4)