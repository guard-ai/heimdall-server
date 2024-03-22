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
    def __init__(self):
        pass
    
    def aggregate_gpt_call(self, text):
        instance = open_AI()
        if instance.is_incident(text)=="YES":
            return instance.analyze_incident(text)
        else:
            return None

    def re_structure(self, reg, text):
        res = self.aggregate_gpt_call(text)
        r = text_to_tuple(res)
        cur_date = datetime.now().date()
        
        event_instance = eventStruct(
            Id = uuid.uuid4(),
            Level =r[2],
            Location =r[1],
            Category =r[0],
            LogId = uuid.uuid4(),
            CreatedAt= cur_date,
            )
        
        log_instance = logStruct(
            Id = uuid.uuid4(),
            Region = reg,
            Utterance = text,
            CreatedAt = cur_date
            )
        
        data = {
            "Event": event_instance,
            "Log": log_instance
            }
        json_data = json.dumps(data, default=str, indent=4)

        return json_data