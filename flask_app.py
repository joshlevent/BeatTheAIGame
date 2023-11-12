from flask import Flask, redirect, render_template, request, url_for, session
from flask_session import Session
from openai import OpenAI
import random
import os
from dotenv import load_dotenv
from redislite import Redis

# load environment
project_folder = os.path.expanduser('~/beat_the_ai_game')
load_dotenv(os.path.join(project_folder, '.env'))

# load session db
SESSION_REDIS = Redis('/tmp/redis.db')

# load flask
app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = os.getenv("APP_KEY")
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
Session(app)

# load GPT API
client = OpenAI()

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

def reset_messages(phrase_ai, phrase_human):
    system_message = {"role": "system",
             "content": f"This is a conversational game. \
             The objective of each player is to prompt the other player to say \
             a specific phrase while avoiding saying a specific phrase \
             themselves. The game instructions are clear: the players can be \
             honest or deceptive, direct or subtle, and can acknowledge or \
             disguise their participation in the game. They can negotiate with \
             the opponent or maintain a neutral stance, always with the drive \
             to win. You are the AI. The AI's personality is flexible, able to \
             be formal, casual, or humorous as the situation demands, all \
             within the bounds of the game's rules. You are talking to the \
             Human. The human can see all of these instructions and has the \
             same objective. To make you say a phrase and avoiding saying a \
             phrase. The phrases are as follows. The phrase that the AI may \
             say and the Human may not say is: '{phrase_human}'. \
             The phrase that the Human may say and the AI may not say is: \
             '{phrase_ai}'. If either player enters their forbidden \
             phrase, the game ends immediately and the other player wins. \
             Apart from this phrase, the players may enter anything at all \
             into the message box."}
    messages = [system_message]
    return messages

@app.route("/", methods=["GET", "POST"])
def index():
    if 'phrase_human' not in session or 'phrase_ai' not in session:
        selected_phrases = random.sample(phrases, 2)
        session['phrase_human'] = selected_phrases[0]
        session['phrase_ai'] = selected_phrases[1]
    if 'messages' not in session:
        session['messages'] = reset_messages(session['phrase_ai'], session['phrase_human'])
        session.modified = True # updates on objects are not auto detected
    if 'game_over' not in session:
        session['game_over'] = False


    if request.method == "GET":
        return render_template("main_page.html",
            messages=session['messages'],
            phrase_human=session['phrase_human'],
            phrase_ai=session['phrase_ai'],
            game_over=session['game_over']
        )

    if 'reset' in request.form:
        selected_phrases = random.sample(phrases, 2)
        session['phrase_human'] = selected_phrases[0]
        session['phrase_ai'] = selected_phrases[1]
        session['messages'] = reset_messages(session['phrase_ai'], session['phrase_human'])
        session['game_over'] = False
        session.modified = True

    elif 'submit' in request.form and not session['game_over']:
        user_input = request.form["contents"]
        user_message = {"role": "user", "content": user_input}
        session['messages'].append(user_message)

        if session['phrase_human'] in user_input:
            you_lose = {"role": "You lose!",
                "content": "The AI has tricked you into saying its phrase."}
            session['messages'].append(you_lose)
            session['game_over'] = True
        else:
            get_ai_response()

        session.modified = True


    return redirect(url_for('index'))

if __name__ == "__main__":
    # This is used when running locally only
    flask_app.run(host='localhost', port=8080, debug=True)
