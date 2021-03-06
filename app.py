# Before Run, install Flask, requests, pymongo, python-dotenv. It uses MongoDB
import requests
from flask import Flask, render_template, jsonify, request, session, redirect

# dotenv 사용 연습 (.env 파일은 .gitignore 로 항상 빼주기!)
from dotenv import load_dotenv
import os

load_dotenv()
CLIENT_ID = os.getenv("CLIENTID")
REDIRECT_URI = os.getenv("REDIRECTURI")
KAKAO_SECRETKEY = os.getenv("KAKAOSECRETKEY")

# Flask app 설정
app = Flask(__name__)

# 임시 데이터 관리용 time
import time

# session 시크릿 키(실제로 사용 되는 서버는 .env 로 숨겨야 한다.)
app.secret_key = 'VerySecretKey'

from pymongo import MongoClient

# localhost 용 MongoDB 연결
client = MongoClient("localhost", 27017)

# 서버용 MongoDB 연결
# client = MongoClient('mongodb://test:test@localhost', 27017)

db = client.sideprojectlogin


# HTML 화면 렌더링
@app.route("/")
def home():
    if "userID" in session:
        return render_template("index.html", username=session.get("userID"), login=True)
    else:
        return render_template("index.html", login=False, )


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


@app.route("/edit")
def edit():
    if "userID" in session:
        return render_template("edit.html", username=session.get("userID"), login=True)
    else:
        return render_template("view.html", login=False)


# 유저 생성

@app.route("/join", methods=["POST"])
def save_user():
    name_receive = request.form['name_give']
    email_receive = request.form['email_give']
    id_receive = request.form["id_give"]
    pw_receive = request.form["pw_give"]

    doc = {
        "name": name_receive,
        "email": email_receive,
        "id": id_receive,
        "pw": pw_receive
    }
    print(doc)
    db.users.insert_one(doc)

    return jsonify({"msg": "생성 완료"})


# 로그인

@app.route("/index", methods=["POST"])
def login():
    id_receive = request.form["id_give"]
    pw_receive = request.form["pw_give"]

    id_user = db.users.find_one({'id': id_receive})
    pw_user = db.users.find_one({'pw': pw_receive})
    print("Login Check:", id_user["id"], pw_user["pw"])
    # id, pw 일치 확인
    if id_user is None or pw_user is None:
        print("Wrong Account")
        return redirect("/")
    else:
        print("Correct Account")
        # 세션에 id 저장하기
        session["userID"] = id_receive
        # 세션 확인
        print(session)
        return redirect("/")


# 세션 삭제

@app.route("/logout")
def logout():
    session.pop("userID")
    return redirect("/")


# 게시글 작성

@app.route("/write", methods=["POST"])
def save_write():
    title_receive = request.form["title_give"]
    content_receive = request.form["content_give"]
    username = session.get("userID")
    secs = str(time.time())
    print(secs)

    # 데이터베이스에 저장
    doc = {
        "time": secs,
        "title": title_receive,
        "content": content_receive,
        "username": username
    }
    print(doc)
    db.noticeboard.insert_one(doc)

    return jsonify({"msg": "생성 완료"})


# 게시글 표시

@app.route("/show", methods=["GET"])
def show_write():
    noticeboards = list(db.noticeboard.find({}, {"_id": False}))
    # idtest = db.noticeboard.find_one({})
    # print(idtest["_id"])
    return jsonify({"all_noticeboards": noticeboards, })


# 게시글 삭제

@app.route("/delete", methods=["POST"])
def delete_noticeboards():
    db.noticeboard.delete_many({})
    print("모든 게시글 제거")
    return redirect("/")


# 게시글 보기

# 1. 해당 게시글의 id(time)값을 알아낸다.
# 2. db에서 해당 게시글과 id가 동일한 데이터를 찾는다.
# 3. 데이터를 가져와 return 해준다.
# 4. html에서 가져온 데이터를 토대로 게시글을 띄워준다.

@app.route("/show_noticeboard", methods=["POST"])
def show_noticeboard():
    id_receive = request.form["id_give"]
    print(id_receive)
    board = db.noticeboard.find_one({"time": id_receive}, {"_id": False})
    print(board)
    return jsonify({"board": board})


# 게시글 수정

# 1. 수정할 게시글의 id(time)값을 알아낸다.
# 2. db에서 해당 게시글과 id가 동일한 데이터를 찾는다.
# 3. 데이터를 가져와 return 해준다.
# 4. html에서 가져온 데이터를 토대로 DB를 수정한다.

@app.route("/edit_noticeboard", methods=["POST"])
def edit_noticeboard():
    id_receive = request.form["id_give"]
    print(id_receive)
    board = db.noticeboard.find_one({"time": id_receive}, {"_id": False})
    print(board)
    return jsonify({"board": board})


@app.route("/save_edit", methods=["POST"])
def save_edit():
    title_receive = request.form["title_give"]
    content_receive = request.form["content_give"]
    id_receive = request.form["id_give"]
    db.noticeboard.update_one({'time': id_receive}, {'$set': {'title': title_receive, "content": content_receive}})
    return jsonify({"msg": "수정 완료!"})

# 카카오 소셜 로그인 코드 받아오기
@app.route("/code", methods=["GET"])
def code():
    code_url = f"https://kauth.kakao.com/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    return redirect(code_url)

# 코드를 이용해 토큰 받아오기
@app.route("/oauth", methods=["GET"])
def token():
    CODE = request.args.get("code")
    token_request = requests.post(f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&code={CODE}&client_secret={KAKAO_SECRETKEY}")
    token_json = token_request.json()
    print(token_json)
    access_token = token_json.get("access_token")
    print(access_token)
    # 유저 정보 가져오기
    userdata = requests.get("https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"})
    print(userdata.json())
    return redirect("/")

# 카카오 로그아웃
@app.route("/kakao-logout")
def kakao_logout():
    # logout = requests.post("https://kapi.kakao.com/v1/user/logout", headers={"Authorization": f"Bearer {access_token}"})
    return redirect("/")

# 포트

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
