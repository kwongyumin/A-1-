import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for



app = Flask(__name__)

from pymongo import MongoClient

client = MongoClient("mongodb+srv://test:sparta@cluster0.u3t9k.mongodb.net/Cluster0?retryWrites=true&w=majority")
db = client.miniProject

# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'SPARTA'


# db컬렉션은 회원정보를 담을 users
# 게시판 정보를 담을 board 를 사용!

# 로그인-> JWT토큰 -> 세션 유지 가능!

# num : 게시물 index 번호!
# name : 게시자 이름
# title : 제목
# content : 내용

# mongoDB -> 외래키 사용 여부 ! /

# API 설계

# 각 페이지로 렌더링
# 최초 접속 시 로그인 화면
# 로그인 성공 시에는 main 페이지로 이동!
# 회원가입 후에는 로그인 페이지로 다시 이동 후 로그인 성공 시 main페이지로 이동
# 로그인이 실패한다면 다시 로그인 페이지

# 로그인 강의 완강 후 다시 확인해보기
# 최상위 수정필요

#flask에서 html 렌더링 시 -> nickname값이 안넘어감
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('index.html', nickname=user_info["nick"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 해당 url 요청 -> 메인페이지 렌더링
@app.route('/main')
def main():
    return render_template('index.html')


# 작성폼으로 렌더링
@app.route('/writeForm')
def write():
    return render_template('writeForm.html')


# 단일객체 렌더링
@app.route('/ObjectView/<num>')
def view(num):
    token_receive = request.cookies.get('mytoken')
    try:
        # 쿠키에 있는 유저의 정보를 읽어옴
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # 읽어온 유저의 id를 통해서 db에서 나머지 정보 찾기
        user_info = db.user.find_one({"username": payload["id"]})
        print(user_info)

        # board db에서 해당 num값에 해당하는 dic 찾아오기
        post = db.board.find_one({'num': int(num)}, {'_id': False})

        # 쿠키에 있는 유저의 아이디와 board에 있는 게시물의 id가 같으면 Ture
        # 외래키를 nick으로 설정하면 post["nick"]으로 변경해야함
        status = post["id"] == payload["id"]

        return render_template('ObjectView.html', user_info=user_info, post=post, num=num, status=status)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# 로그인 폼으로 렌더링, msg 파라미터를 같이 전달
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


# 회원가입 폼으로 렌더링, 토글은 아직 사용 안함,
@app.route('/register')
def register():
    return render_template('register.html')


# 회원가입 api /회원 정보를 받아 비밀번호를 해쉬 처리하여 db에 저장
@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})

    return jsonify({'result': 'success'})


# 로그인 api

@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # db에는 현재 해당 아이디의 비밀번호가 해쉬처리 되어있으므로 , 로그인 시에도 해쉬처리 필요
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된 pw를 가지고 해당 유저 찾기
    result = db.user.find_one({'id': id_receive}, {'pw': pw_hash})
    # 1 .해당 유저가 있다면..
    if result is not None:
        # payload 만료 시간 3600 초 변경필요
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60*60)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({"result": "success", "token": token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 전체 후기 조회 /Get방식 메서드를 이용 새로고침 시 전체목록을 가져온다.
# DB에 더미데이터 집어넣어서 확인하기
@app.route("/boardList", methods=["GET"])
def board_list():
    boardList = list(db.board.find({}, {'_id': False}))

    return jsonify({'boardlist': boardList})


# 작성란 -> 내용들을 DB에 저장!

@app.route('/write', methods=['POST'])
def insert_content():
    # 넘버링
    count = list(db.board.find({}, {'_id': False}))
    num = len(count) + 1

    # 파라미터값 받기
    file = request.files["file_give"]
    title_receive = request.form['title_give']
    content_receive = request.form['content_give']

    extension = file.filename.split('.')[-1]

    today = datetime.datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    filename = f'file-{mytime}'

    save_to = f'static/userImg/{filename}.{extension}'
    file.save(save_to)

    doc = {
        'num': num,
        'title': title_receive,
        'content': content_receive,
        'file': f'{filename}.{extension}'
    }

    db.board.insert_one(doc)

    return jsonify({'msg': '작성 완료!'})

# 포스트 삭제
@app.route('/api/delete_post', methods=['POST'])
def delete_word():
    num_receive = request.form["num_give"]
    db.board.delete_one({"num": int(num_receive)})
    return jsonify({'result': 'success', 'msg': '포스트 삭제ㅠ'})







if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

