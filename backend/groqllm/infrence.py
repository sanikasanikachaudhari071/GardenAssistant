from groq import Groq
from groq.types.chat.chat_completion import ChatCompletion
from typing import List, Dict
import os

class groqinference:
    # def __init__(self, model: str = "llama-3.2-11b-vision-preview") -> None:
    #     os.environ["GROQ_API_KEY"] = os.getenv("groq_api_key")
    #     self.groq_client = Groq()
    #     self.model = model

    # def generate_responce(self,
    #     messages: List[Dict[str, str]],
    #     temperature=1,
    #     max_completion_tokens=1024,
    #     top_p=1,
    #     stream=False,
    #     stop: List[str] = None,
    #     ) -> str:

    #     """
    #     Generate a response using Groq's LLM.

    #     Args:
    #         messages: List of message dictionaries with 'role' and 'content' keys

    #     Returns:
    #         str: The generated response from the model
    #     """
    #     completion: ChatCompletion = self.groq_client.chat.completions.create(
    #         model="llama-3.2-11b-vision-preview",
    #         messages=messages,
    #         temperature=temperature,
    #         max_completion_tokens=max_completion_tokens,
    #         top_p=top_p,
    #         stream=stream,
    #         stop=stop,
    #     )
    #     return completion.choices[0].message.content

    def __init__(self, model: str = "llama-3.2-11b-vision-preview"):
        self.groq_client = Groq(api_key=os.getenv("groq_api_key"))
        self.model = model
    
    def generate_responce(self, messages: List[Dict], temperature=1, max_completion_tokens=1024):
        try:
            completion = self.groq_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_completion_tokens
            )
            return completion.choices[0].message.content
        except Exception as e:
            print("Error generating response:", e)  # Debugging line
            return "Error generating response."