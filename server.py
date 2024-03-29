from flask import Flask, request
import os
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key="key"
)

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/input', methods=['POST'])
def get_input():
    if request.method == 'POST':
        data = request.json

        chat_completion = client.chat.completions.create(
            messages=data.messages,
            model="gpt-3.5-turbo",
        )

        return chat_completion.choices[0].message.content



