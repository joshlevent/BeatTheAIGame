from flask import Flask, redirect, render_template, request, url_for
from openai import OpenAI
import random
import os

os.environ['OPENAI_API_KEY'] = "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"

app = Flask(__name__)
app.config["DEBUG"] = True

game = True

phrases = [
    "Leaves fall in autumn",
    "Raindrops on roses",
    "Books line the shelf",
    "Cats nap peacefully",
    "Dogs chase balls",
    "Tea warms the soul",
    "Stars twinkle above",
    "Friends laugh together",
    "Music fills the air",
    "Snowflakes drift down",
    "Children play outside",
    "Bakers knead dough",
    "Gardens bloom brightly",
    "Fireflies glow at dusk",
    "Sunsets paint the sky",
    "Clocks tick steadily",
    "Waves hug the shore",
    "Mountains reach high",
    "Kites dance on wind",
    "Cookies bake golden"
]

selected_phrases = random.sample(phrases, 2)

client = OpenAI()
phrase_human = selected_phrases[0]
phrase_ai = selected_phrases[1]

system_message = {"role": "system",
             "content": f"You are the AI. You are talking to the human. Your goal \
             is to make the Human output the \
             following phrase: '{phrase_human}', and avoid entering the following \
             phrase into the chat: '{phrase_ai}'. If you enter this phrase, you lose \
             the game and the Human wins. Apart from this phrase, you may enter \
             anything at all into the message box."}

messages = [system_message]

def get_ai_response():
  completion = client.chat.completions.create(
    model="gpt-4-1106-preview",
    messages=messages
  )
  ai_message = completion.choices[0].message
  messages.append(ai_message)
  if phrase_ai in ai_message.content:
    ai_lose = {"role": "The AI lost!",
             "content": "You tricked the AI into saying your phrase."}
    messages.append(ai_lose)
  return

@app.route("/", methods=["GET", "POST"])
def index(messages=messages):
    if request.method == "GET":
        return render_template("main_page.html", messages=messages, phrase_human=phrase_human, phrase_ai=phrase_ai)
    if 'reset' in request.form:
        messages = [system_message]
    elif 'submit' in request.form:
        user_input = request.form["contents"]
        user_message = {"role": "user",
                 "content": user_input}
        messages.append(user_message)
        if phrase_human in user_input:
            you_lose = {"role": "You lose!",
                 "content": "The AI has tricked you into saying its phrase."}
            messages.append(you_lose)
        else:
            get_ai_response()
    return redirect(url_for('index'))