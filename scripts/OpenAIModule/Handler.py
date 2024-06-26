import time
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIChatBot:
    def __init__(self, api_key, assistant_id):
        self.client = OpenAI(api_key=api_key)
        self.assistant_id = assistant_id

    def create_chat(self, user_message):
        self.chat = self.client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message,
                }
            ]
        )
        
        self.run = self.client.beta.threads.runs.create(thread_id=self.chat.id, assistant_id=self.assistant_id)
        print(f"👉 Run Created: {self.run.id}")
        self._wait_for_completion()

    def _wait_for_completion(self):
        while self.run.status != "completed":
            self.run = self.client.beta.threads.runs.retrieve(thread_id=self.chat.id, run_id=self.run.id)
            print(f"⏳ Run Status: {self.run.status}")
            time.sleep(0.5)
        print(f"🏁 Run Completed!")
        self._retrieve_latest_message()

    def _retrieve_latest_message(self):
        message_response = self.client.beta.threads.messages.list(thread_id=self.chat.id)
        messages = message_response.data
        latest_message = messages[0]
        print(f"🤖 Response: {latest_message.content[0].text.value}")

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("ASSISTANT_ID")
bot = OpenAIChatBot(api_key, assistant_id)
# bot.create_chat([
#     {
#         "type": "text",
#         "text": "Who is the greatest businessman of all time?"
#     }
# ])

# Caso de uso com texto e imagem
bot.create_chat([
    {
        "type": "text",
        "text": "What is this an image of?"
    },
    {
        "type": "image_url",
        "image_url": {
            "url": "https://upload.wikimedia.org/wikipedia/en/a/a9/Example.jpg",
            "detail": "high"
        }
    }
])
