import openai
import json

# robust function calling works for gpt-4-0613 or later

def get_parameters(location):
    """Get Parameters"""
    incident = {
        "location": location,
        "category": ["crime", "fire", "traffic", "medical", "hazards", "suspicious activity", "protests", "public assistance", "other"],
        "level_of_threat": ["1 low-risk", "2 moderate-risk", "3 high-risk"],
    }
    return json.dumps(incident)

class OpenAIFunctionClient(object):
    def __init__(self, region):
        self.region = region

    def run_(self, call):
        completion = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[{"role": "user", "content": "Listen to the following radio communication from "+self.region+", and record an incident: "+ call}],
            functions=[
            {
                "name": "get_parameters",
                "description": "Get a list of parameters for an incident",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "parameters": {
                            "type": "array",
                            "location": {
                                "type": "string",
                                "description": "a very specific location of the incident base on the region"
                            },
                            "category": {
                                "type": "string",
                                "description": "category of incident: crime, fire, traffic, medical, hazards, suspicious activity, protests, public assistance, other"
                            },
                            "level_of_threat": {
                                "type": "string",
                                "description": "the level of threat for the indicident: 1 low-risk, 2 moderate-risk, 3 high-risk"
                            },
                            "description": "List of parameters that describe the incident"
                        }
                    },
                    "required": ["parameters"]
                }
            }
            ],
            function_call={"name": "get_parameters"} or "auto",
        )
        reply_content = completion.choices[0].message
        funcs = reply_content.to_dict()['function_call']['arguments']
        funcs = json.loads(funcs)
        return funcs['parameters'] # list [location, category, level_of_threat]
