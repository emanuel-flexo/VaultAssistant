import time
import os
import streamlit as st
import tempfile
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

class OpenAIChatBot:
    def __init__(self, api_key, assistant_id):
        self.client = OpenAI(api_key=api_key)
        self.assistant_id = assistant_id

    def create_file(self, image_path:str):
        try:
            return self.client.files.create(
                file=open(image_path, "rb"),
                purpose="vision"
                )
        except Exception as er0:
            print("ERRO EM CREATE_FILE : ", er0 )
            return None
        
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

        if isinstance(latest_message.content, list):
            responses = []
            for content in latest_message.content:
                if content.type == 'text':
                    responses.append(f"{content.text.value}")
                elif content.type == 'image_url':
                    responses.append(f"Image URL: {content.image_url.url} - Detail: {content.image_url.detail}")
            return responses
        else:
            return [f"🤖 {latest_message.content}"]

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("ASSISTANT_ID")
# Configuração da interface Streamlit
st.title("VaultAI ChatBot")
st.write("Envie uma mensagem de texto ou carregue uma imagem para interagir com o bot.")

bot = OpenAIChatBot(api_key, assistant_id)

user_message = st.text_area("Mensagem de Texto")

uploaded_file = st.file_uploader("Carregar uma imagem", type=["png", "jpg", "jpeg"])
if uploaded_file:
    temp_dir = tempfile.mkdtemp()
    path = os.path.join(temp_dir, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getvalue())
    st.image(path)
    
if st.button("Enviar Mensagem"):
    if user_message:
        message_content = [{"type": "text", "text": user_message}]
    
        file= bot.create_file(path)
        image_file = file.id 
        if user_message:
            message_content.append({"type": "image_file", 
                                    "image_file": {"file_id": image_file}})
        else:
            message_content = [{"type": "image_file", 
                                "image_file": {"file_id": image_file}}]
    
    bot.create_chat(message_content)
    responses = bot._retrieve_latest_message()

    st.write("Resposta 🤖:")
    for response in responses:
        st.write(response)

