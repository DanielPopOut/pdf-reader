from flask import Flask, request
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
OPEN_AI_API_KEY = os.environ.get("OPEN_AI_API_KEY")

app = Flask(__name__)

client = OpenAI(
    # This is the default and can be omitted
    api_key=OPEN_AI_API_KEY,
)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/input", methods=["POST"])
def get_input():
    if request.method == "POST":
        data = request.json

        messages = data["messages"]

        chat_completion = client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo",
        )

        result = chat_completion.choices[0].message.content
        return {"result": result}
