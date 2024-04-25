from flask import Flask, request, redirect, url_for
import os
from openai import OpenAI
from dotenv import load_dotenv
import PyPDF2

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
        "content": f"Take each step from the roadmap and create a graph using svg: {result}",
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

        print(roadmap)
        graph = generate_graph(roadmap)
        print(graph)
        # # render the graph as jpg
        # dot = graphviz.Source(graph)
        # graph_as_jpg = dot.render('roadmap', format='jpeg', view=True)
        return graph


def check_user_preferences_are_done(messages):
    # if we have one message from the bot and it contains question_to_ask and the next message contains no then we are done
    if len(messages) > 1:
        last_user_message = messages[-1]
        last_bot_message = messages[-2]
        print(
            last_user_message,
            last_bot_message,
            "no" in last_user_message["content"].lower(),
        )
        if (question_to_ask.lower()) in last_bot_message[
            "content"
        ].lower() and "no" in last_user_message["content"].lower():
            return True
    return False


def filter_and_propose_pizzas(messages):
    # finding bot message with anything else inside
    # checking if next user message is no

    ##
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
    )
    return False


question_to_ask = """Anything else"""


def continue_chat_with_user(messages):
    systemPrompt = f'''You are a pizza waiter and you need to get the user's preferences.
You need to know the size, toppings, and crust.
Ask the questions one by one.
Once the user has expressed his preferences, ask him if he is done with this very specific question "{question_to_ask}"'''
    messages_to_use = [{"role": "system", "content": systemPrompt}] + messages
    chat_completion = client.chat.completions.create(
        messages=messages_to_use,
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content


# Pizza project
@app.route("/pizza_bot", methods=["POST"])
def handle_pizza_messages():
    if request.method == "POST":
        data = request.json

        messages = data["messages"]

        ## check if user has finished expressing his preferences
        has_user_expressed_preferences = check_user_preferences_are_done(messages)
        ## if yes, generate the order
        if has_user_expressed_preferences:
            return {"result": "hello"}
        else:
            ## if no, ask for more preferences

            result = continue_chat_with_user(messages)
            return {"result": result}
