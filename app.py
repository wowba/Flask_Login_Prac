# Before Run, install Flask, requests, pymongo. It uses MongoDB

from flask import Flask, render_template, jsonify, request, session

app = Flask(__name__)

# session 시크릿 키
app.secret_key = 'VerySecretKey'

from pymongo import MongoClient

client = MongoClient("localhost", 27017)
db = client.sideprojectlogin

## HTML 화면 렌더링
@app.route("/")
def home():
    if "userID" in session:
        return render_template("index.html",username = session.get("userID"),login = True)
    else:
        return render_template("index.html",login = False)

@app.route("/join")
def join():
    return render_template("join.html")

@app.route("/mypage")
def mypage():
    return render_template("mypage.html")

## 유저 생성

@app.route("/join", methods=["POST"])
def save_user():
    name_receive = request.form['name_give']
    email_receive = request.form['email_give']
    id_receive = request.form["id_give"]
    pw_receive = request.form["pw_give"]

    doc = {
        "name":name_receive,
        "email":email_receive,
        "id":id_receive,
        "pw":pw_receive
    }
    print(doc)
    db.users.insert_one(doc)
    
    return jsonify({"msg": "생성 완료"})

## 로그인

@app.route("/index",methods=["POST"])
def login():
    id_receive = request.form["id_give"]
    pw_receive = request.form["pw_give"]

    id_user = db.users.find_one({'id': id_receive})
    pw_user = db.users.find_one({'pw': pw_receive})
    print("Login Check:",id_user,pw_user)
        ## id, pw 일치 확인
    if id_user == None or pw_user == None:
        print("Wrong Account")
        return render_template("index.html")
    else:
        print("Correct Account")
        ## 세션에 id 저장하기
        session["userID"] = id_receive
        ## 세션 확인
        print(session)

        return render_template("index.html")

@app.route("/logout")
def logout():
    ## 세션 삭제
    session.pop("userID")
    return render_template("index.html")

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)