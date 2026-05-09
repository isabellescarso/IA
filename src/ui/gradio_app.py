import os
import requests
import gradio as gr
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")
AVAILABLE_MODELS = ["llama3.2", "mistral"]


class AskApiClient:
    def __init__(self, base_url: str):
        self._base_url = base_url

    def ask(self, question: str, model: str) -> str:
        response = requests.post(
            f"{self._base_url}/ask",
            json={"question": question, "model": model},
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["answer"]


class GradioInterface:
    def __init__(self, client: AskApiClient):
        self._client = client

    def answer(self, question: str, model: str) -> str:
        return self._client.ask(question, model)

    def build(self) -> gr.Interface:
        return gr.Interface(
            fn=self.answer,
            inputs=[
                gr.Textbox(label="Pergunta", placeholder="Ex: Quais registros apresentam glicose elevada?"),
                gr.Dropdown(choices=AVAILABLE_MODELS, value=AVAILABLE_MODELS[0], label="Modelo"),
            ],
            outputs=gr.Textbox(label="Resposta"),
            title="CGMacros RAG",
            description="Consulta inteligente sobre dados de glicose e nutrição.",
        )


client = AskApiClient(API_URL)
interface = GradioInterface(client)
app = interface.build()

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)