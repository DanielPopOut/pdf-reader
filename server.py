from flask import Flask, request, redirect, url_for
import os
from openai import OpenAI
from dotenv import load_dotenv
import PyPDF2
import graphviz

load_dotenv()  # take environment variables from .env.
OPEN_AI_API_KEY = os.environ.get("OPEN_AI_API_KEY")

app = Flask(__name__)

client = OpenAI(
    # This is the default and can be omitted
    api_key=OPEN_AI_API_KEY,
)

upload_page = """
<form action="/upload_pdf" method="post" enctype="multipart/form-data">
    <label for="file">Choose a file to upload:</label>
    <input type="file" id="file" name="file">
    <br>
    <input type="submit" value="Upload File">
</form>
"""


@app.route("/upload_pdf", methods=["POST"])
def upload():
    if request.method == "POST":
        file = request.files.get("file")

        reader = PyPDF2.PdfReader(file)

        # Initialize an empty string to collect text
        text = ""

        # Iterate over each page
        for page_num in range(len(reader.pages)):
            # Get a specific page in the PDF
            page = reader.pages[page_num]

            # Extract text from the page
            text += page.extract_text()
        return summarize_text(text)


@app.route("/")
def hello_world():
    return upload_page


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


def generate_roadmap(text: str):
    messageBase = {
        "role": "system",
        "content": f"Give me a 10 step roadmap to learning {text}. Break each step 3 sub portions.",
    }
    allMessages = [messageBase]

    chat_completion = client.chat.completions.create(
        messages=allMessages,
        model="gpt-3.5-turbo",
    )

    result = chat_completion.choices[0].message.content
    return result

def generate_graph(result):
    messageBase = {
        "role": "system",
        "content": f"Take each step from the roadmap and create a graph using networkx. {result}",
    }
    allMessages = [messageBase]

    chat_completion = client.chat.completions.create(
        messages=allMessages,
        model="gpt-3.5-turbo",
    )

    result = chat_completion.choices[0].message.content
    return result


learning_form = """
<div> 
<form style="width:300px;margin:auto;" action="/get_roadmap" method="post" enctype="multipart/form-data">
    <label for="file">What do you want to learn:</label>
    <input id="query" name="query">
    <br>
    <input type="submit" value="Submit">
</form>
</div>
"""


# Step 1 show the input
@app.route("/learn")
def learning_form_fn():
    return learning_form


# Step 2 get the input and retrieve the roadmap


@app.route("/get_roadmap", methods=["POST"])
def get_roadmap():
    if request.method == "POST":
        body = request.form.get("query")

        ## Ask chatgpt the roadmap

        ## format the roadmap
        roadmap = generate_roadmap(body)
        graph = generate_graph(roadmap)
        # # render the graph as jpg
        # dot = graphviz.Source(graph)
        # graph_as_jpg = dot.render('roadmap', format='jpeg', view=True)
        return graph
