from flask import Flask, redirect, render_template, request, url_for, session
from openai import OpenAI
import random
import os
from dotenv import load_dotenv
project_folder = os.path.expanduser('~/beat_the_ai_game')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = os.getenv("APP_KEY")

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



client = OpenAI()



def get_ai_response():
    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=session['messages']
    )
    ai_content = completion.choices[0].message.content
    ai_message = {"role": "assistant",
             "content": ai_content}
    session['messages'].append(ai_message)
    if session['phrase_ai'] in ai_content:
        ai_lose = {"role": "The AI lost!",
                   "content": "You tricked the AI into saying your phrase."}
        session['messages'].append(ai_lose)
        session['game_over'] = True
    return

@app.route("/", methods=["GET", "POST"])
def index():
    if 'phrase_human' not in session or 'phrase_ai' not in session:
        selected_phrases = random.sample(phrases, 2)
        session['phrase_human'] = selected_phrases[0]
        session['phrase_ai'] = selected_phrases[1]
        session.modified = True
    if 'messages' not in session:
        system_message = {"role": "system",
             "content": f"You are the AI. You are talking to the Human. Your goal \
             is to make the Human output the \
             following phrase: '{session['phrase_human']}', and avoid entering the following \
             phrase into the chat: '{session['phrase_ai']}'. If you enter this phrase, you lose \
             the game and the Human wins. Apart from this phrase, you may enter \
             anything at all into the message box."}
        session['messages'] = [system_message]
        session.modified = True
    if 'game_over' not in session:
        session['game_over'] = False
        session.modified = True


    if request.method == "GET":
        return render_template("main_page.html", messages=session['messages'], phrase_human=session['phrase_human'], phrase_ai=session['phrase_ai'], game_over=session['game_over'])

    if 'reset' in request.form:
        selected_phrases = random.sample(phrases, 2)
        session['phrase_human'] = selected_phrases[0]
        session['phrase_ai'] = selected_phrases[1]
        system_message = {"role": "system",
             "content": f"You are the AI. You are talking to the Human. Your goal \
             is to make the Human output the \
             following phrase: '{session['phrase_human']}', and avoid entering the following \
             phrase into the chat: '{session['phrase_ai']}'. If you enter this phrase, you lose \
             the game and the Human wins. Apart from this phrase, you may enter \
             anything at all into the message box."}
        session['messages'] = [system_message]
        session['game_over'] = False
        session.modified = True

    elif 'submit' in request.form and not session['game_over']:
        user_input = request.form["contents"]
        user_message = {"role": "user", "content": user_input}
        session['messages'].append(user_message)

        if session['phrase_human'] in user_input:
            you_lose = {"role": "You lose!", "content": "The AI has tricked you into saying its phrase."}
            session['messages'].append(you_lose)
            session['game_over'] = True
        else:
            get_ai_response()

        session.modified = True


    return redirect(url_for('index'))
