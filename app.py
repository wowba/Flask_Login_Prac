# Before Run, install Flask, requests, pymongo. It uses MongoDB

from flask import Flask, render_template, jsonify, request, session , redirect

app = Flask(__name__)

# session 시크릿 키
app.secret_key = 'VerySecretKey'

from pymongo import MongoClient

# localhost용 MongoDB 연결
client = MongoClient("localhost", 27017)

# 서버용 MongoDB 연결
# client = MongoClient('mongodb://test:test@localhost', 27017)

db = client.sideprojectlogin

# 데이터 관리용 time
import time

## HTML 화면 렌더링
@app.route("/")
def home():
    if "userID" in session:
        return render_template("index.html",username = session.get("userID"),login = True,)
    else:
        return render_template("index.html",login = False,)

@app.route("/join")
def join():
    if "userID" in session:
        return render_template("join.html", username=session.get("userID"), login=True)
    else:
        return render_template("join.html", login=False)

@app.route("/write")
def write():
    if "userID" in session:
        return render_template("write.html", username=session.get("userID"), login=True)
    else:
        return render_template("join.html", login=False)

@app.route("/view")
def view():
    if "userID" in session:
        return render_template("view.html", username=session.get("userID"), login=True)
    else:
        return render_template("view.html", login=False)

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
    print("Login Check:",id_user["id"],pw_user["pw"])
        ## id, pw 일치 확인
    if id_user == None or pw_user == None:
        print("Wrong Account")
        return redirect("/")
    else:
        print("Correct Account")
        ## 세션에 id 저장하기
        session["userID"] = id_receive
        ## 세션 확인
        print(session)
        return redirect("/")

## 세션 삭제

@app.route("/logout")
def logout():
    session.pop("userID")
    return redirect("/")


## 게시글 작성

@app.route("/write", methods=["POST"])
def save_write():
    title_receive = request.form["title_give"]
    content_receive = request.form["content_give"]
    username = session.get("userID")
    secs = str(time.time())
    print(secs)

    ## 데이터베이스에 저장
    doc = {
        "time":secs,
        "title":title_receive,
        "content":content_receive,
        "username":username
    }
    print(doc)
    db.noticeboard.insert_one(doc)

    return jsonify({"msg": "생성 완료"})

## 게시글 표시

@app.route("/show", methods=["GET"])
def show_write():
    noticeboards = list(db.noticeboard.find({},{"_id":False}))
    return jsonify({"all_noticeboards":noticeboards})

## 게시글 삭제

@app.route("/delete", methods=["POST"])
def delete_noticeboards():
    db.noticeboard.delete_many({})
    print("모든 게시글 제거")
    return redirect("/")

## 게시글 보기

## 포트

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)