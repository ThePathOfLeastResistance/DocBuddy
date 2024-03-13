from flask import Flask, render_template, session, request, flash, redirect
from flask_session import Session
import requests
from cs50 import SQL
import os
from werkzeug.security import check_password_hash, generate_password_hash
import os
import secrets
from functools import wraps

os.environ["SQLITE3_BINARY"] = "/nix/store/ypmlb10yyizd22cmclqmyqpydal24mfx-sqlite-3.41.2-bin/bin/sqlite3"

app = Flask(__name__)
secret_key=secrets.token_hex(16)
app.secret_key= secret_key
db = SQL("sqlite:///users.db")

talkList = []



@app.route('/login', methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
      rows = db.execute("SELECT * FROM users WHERE email = ?", (request.form["email"],))
      if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
          return render_template("login.html")
      else:
          session["user_id"] = rows[0]["id"]
          return render_template("home.html")
      session["user_id"] = rows[0]["id"]
    return render_template("login.html")
  
@app.route('/index', methods=["GET"])
def index():
    if request.method=="GET":
      return render_template("index.html")


@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        session.clear()
        return render_template("signup.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        job = request.form.get("job")
        birth = request.form.get("birth")
        number = request.form.get("number")
        gender = request.form.get("gender")
        race = request.form.get("race")
        issues = request.form.get("issues")
        if not password or not email:
          return render_template("signup.html")
        else:
          hash = generate_password_hash(password)
          db.execute("INSERT INTO users (email, hash, job, birth, number, gender, race, issues) VALUES (:email, :hash, :job, :birth, :number, :gender, :race, :issues)", email = email, hash = hash, job = job, birth=birth, number=number, gender=gender, race=race, issues=issues)
          flash("You've been signed up!")
        return render_template("login.html")
    return render_template("signup.html")

@app.route('/')
def home():
    return render_template("home.html")
  
@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")



import openai

openai.api_key = os.environ['apki2']

message_history = [{"role": "user", "content": f"imagine you are given the knowledge of medicine and everything that a doctor needs to know. You are going to take the role of {type}. I make up a person with a job occupation, date of birth, gender, race, and past medical issues, and the symptoms they are facing. Reply only with a diagnosis and treatment suggestions based on the input. If you understand, say OK."}, {"role": "assistant", "content": f"OK"}]

def change(message_history, type, person):
  return {"role": "user", "content": f"imagine you are given the knowledge of medicine and everything that a doctor needs to know. You are going to take the role of {type}. Here is a descirption of a imganry freind, I imagine him with a list of character traits in a list, with each vaule in a dictionary, here is the list : {person}. Reply only with a diagnosis, treatment suggestions and/or suggestions on next step based on the information given to you. Make sure to make your response short and conise."}, {"role": "assistant", "content": f"ok, i understand"}, {"role": "user", "content": f" I am a 22-year-old female who often suffers constipation to the point where I feel like I get minor external hemorrhoids that often bleed."}, {"role": "assistant", "content": f"Hello. I think you are overthinking about your symptoms. To be conscious is good but to be over conscious may fall in the category of anxiety and is not good. I will advise you to be relaxed. Based on your symptoms, I do not feel anything to be worried of. Considering your age and symptoms of constipation and feeling something more probably pointing towards hemorrhoids or some local pathology. But physical examination and maybe flexible sigmoidoscopy would be appropriate to confirm underlying pathology or maybe online video consultation with gastroenterologist if you are worried about going to the hospital. I will advise you following general measures to follow that will help you. 1) Try to relax. Do not overthink. There is nothing serious we are thinking of. 2) Take fibers. Increase it in the diet in the form of vegetables. Add Ispagol in your diet. 3) Avoid constipation. 4) Take plenty of water. 5) Do regular walk, exercise inside your home if you can not go outside. 6) Do not strain in the restroom. 7) Take a sitz bath daily. Follow me in case you got further queries."}, {"role": "user", "content": f"What is healther a apple or a cookie"}, {"role": "assistant", "content": f"a apple is healther because there is less sugar and more vitanmes."}, {"role": "user", "content": f"What should I eat to be healther"}, {"role": "assistant", "content": f"What do I need to eat to be healthier? 8 tips for healthy eating Base your meals on higher fibre starchy carbohydrates. ... Eat lots of fruit and veg. ... Eat more fish, including a portion of oily fish. ... Cut down on saturated fat and sugar. ... Eat less salt: no more than 6g a day for adults. ... Get active and be a healthy weight. ... Do not get thirsty. ... Do not skip breakfast."}, {"role": "user", "content": f"What should I do to be healther"}, {"role": "assistant", "content": f"Measure and Watch Your Weight. ... Limit Unhealthy Foods and Eat Healthy Meals. ... Take Multivitamin Supplements. ... Drink Water and Stay Hydrated, and Limit Sugared Beverages. ... Exercise Regularly and Be Physically Active. ... Reduce Sitting and Screen Time. ... Get Enough Good Sleep. ... Go Easy on Alcohol and Stay Sober."}

def chat(inp, type, person):
    message_history.append({"role": "user", "content": f"{inp}"})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=change(message_history, type, person)
    )
    reply_content = completion.choices[0].message.content.rstrip("\n")
    message_history.append({"role": "assistant", "content": f"{reply_content}"})
    return reply_content


@app.route('/talk/<type>', methods =["GET", "POST"])
def talk(type):
    if request.method == "POST":
      input = request.form.get("question")
      user_id = session.get("user_id")
      print(user_id)
      person=db.execute("SELECT * FROM users WHERE id=?",session['user_id'])
      result = chat(input, type, person)
      return render_template("question.html", list = message_history, type = type)
    return render_template("question.html", list = message_history, type = type)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80, debug=True)
