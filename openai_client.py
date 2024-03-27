import openai
import os

OPEN_AI_KEY = os.getenv("OPENAI_KEY")

MODEL = "gpt-3.5-turbo"
SYST = "You are a secretary that is responsible for documenting incidents around the city. Your job is to listen to radio dispatch and document incidents. Follow instructions very closely. If an instruction is unclear, vague, or is not applicable. Respond with “ERROR” and nothing else."
CT1 = "An incident is categorized as something that may be relevant to public safety or an event that people might be intrigued by. If there is an incident to report, respond with YES, else respond with NO. Here is the radio dispatch communication: "
CT2A = "Listen to the following radio dispatch communication: "
CT2B = "\nThis is the end of the dispatch communication, return a simple incident summary in this format: TYPE: category(str) | LOCATION: place(not region, use region to be more specific) | LEVEL: level_of_threat(int). If a variable can not be determined, simply fill it with NA."

SYST_LOC = "You have access to the google maps api, given a region and a location description, simply return the input string needed to get a coordinate with google maps api with nothing else"
LOC = "Given the following region and location description, simply return the input string needed to get a coordinate with google maps api with nothing else: "


class OpenAIClient(object):
    def __init__(self, region):
        self.region = region

    def is_incident(self, coms, temp=1):
        messages = [
            {'role': 'system', 'content': SYST},
            {'role': 'user', 'content': CT1 + coms}
        ]
        response = openai.ChatCompletion.create(
            model=MODEL, messages=messages, temperature=temp, api_key=OPEN_AI_KEY)
        return response['choices'][0]['message']['content'].strip()

    # segregated to increase accuracy of model
    def analyze_incident(self, coms, temp=1):
        messages = [
            {'role': 'system', 'content': SYST},
            {'role': 'user', 'content': CT2A + self.region + coms + CT2B}
        ]
        response = openai.ChatCompletion.create(
            model=MODEL, messages=messages, temperature=temp, api_key=OPEN_AI_KEY)
        return response['choices'][0]['message']['content'].strip()

    # IF LOCATION IS NOT COMPATIBLE, CALL TO TRY AGAIN, ** this prompt needs to be improve, if you are bored....
    def for_google(self, reg, loc_query, temp=1):
        messages = [
            {'role': 'system', 'content': SYST_LOC},
            {'role': 'user', 'content': LOC + reg + ", " + loc_query}
        ]
        response = openai.ChatCompletion.create(
            model=MODEL, messages=messages, temperature=temp, api_key=OPEN_AI_KEY)
        return response['choices'][0]['message']['content'].strip()
