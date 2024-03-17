from dataclasses import dataclass
from gpt_and_struct import open_AI
import json

from datetime import datetime, date


@dataclass
class jsonStruct:
    id: str #str for now, change to "UUID"?
    level: int
    location: str #str for now, change to "point"?
    category: str
    log_id: str #what is the difference id & log?
    created_at: date #make sure this date class is consistent

    region: str
    utterance: str

    def to_json(self):
        return json.dumps(self.__dict__)

def text_to_tuple(res):
    res = res.split('|')
    res = [r.replace(' ', '') for i, r in enumerate(res)]
    res = [r.split(':')[1] for i, r in enumerate(res)] #type, loc, lvl
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

    def re_structure(self, iid, reg, text):
        res = self.aggregate_gpt_call(text)
        r = text_to_tuple(res)
        cur_date = datetime.now().date()
        
        json_instance = jsonStruct(
            id =str, #might have to make a def for this instead of simple pass
            level =r[2],
            location =str, #needs to be updated, same with id (r[1])
            category =r[0],
            log_id =str, #with id
            created_at =cur_date,

            region =reg,
            utterance =text,
            )
        return json_instance