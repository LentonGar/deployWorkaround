 ##Handles OpenAi connnections: isolates API

from openai import OpenAI
from app.config import Config

class AIClient:
    def __init__(self):
        """Initialises OPenAI connection with settings from config"""
        #Initialise client
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        #give client name so it can be accessed later
        self.model = Config.MODEL_NAME

    def get_chat_completion(self, messages, temperature:float=0.7) -> str:
        """
        Sends list of messages to the AI and returns text response

        Args:
        
        messages (list): list of message dictionaries (e.g. [{"role": "user",
        ...}])

        Returns: 

        str: the AIs response text
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model, 
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error communicating with OpenAi: {e}")
            raise e
