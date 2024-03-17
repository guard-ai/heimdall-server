import openai
OPEN_AI_KEY = ''
MODEL = "gpt-3.5-turbo"
SYST = "You are a secretary that is responsible for documenting incidents around the city. Your job is to listen to radio dispatch and document incidents. Follow instructions very closely. If an instruction is unclear, vague, or is not applicable. Respond with “ERROR” and nothing else."
CT1 = "An incident is categorized as something that may be relevant to public safety or an event that people might be intrigued by. If there is an incident to report, respond with YES, else respond with NO. Here is the radio dispatch communication: "
CT2A = "Listen to the following radio dispatch communication: "
CT2B = "\nThis is the end of the dispatch communication, return a simple incident summary in this format: TYPE: category(str) | LOCATION: place(str) | LEVEL: level_of_threat(int). If a variable can not be determined, simply fill it with NA."

class open_AI(object):
    def __init__(self):
        pass
        
    def is_incident(self, coms, temp):
        messages = [
            {'role': 'system', 'content': SYST},
            {'role': 'user', 'content': CT1 + coms}
        ]
        response = openai.ChatCompletion.create(model=MODEL, messages=messages, temperature=temp, api_key=OPEN_AI_KEY)
        return response['choices'][0]['message']['content'].strip() 

    # segregated to increase accuracy of model
    def analyze_incident(self, coms, temp):
        messages = [
            {'role': 'system', 'content': SYST},
            {'role': 'user', 'content': CT2A + coms + CT2B}
        ]
        response = openai.ChatCompletion.create(model=MODEL, messages=messages, temperature=temp, api_key=OPEN_AI_KEY)
        return response['choices'][0]['message']['content'].strip() 