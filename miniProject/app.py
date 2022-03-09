import datetime
import hashlib
from datetime import timedelta

import jwt
from flask import Flask, render_template, jsonify, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

# 토큰 비밀 문자열
SECRET_KEY = 'SPARTA'

client = MongoClient('mongodb+srv://test:sparta@cluster0.u3t9k.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.miniProject


# DB--------------------
# 회원 관련 정보 -> users
# 게시판 관련 정보 -> board


# ------------------------------로그인, 회원가입(중복확인 등)----------------------------------

# 1.토큰 받아오기
# flask에서 html 렌더링 시 -> nickname값이 안넘어갔음
@app.route('/')
def home():
    boardList = list(db.board.find({},{"_id":False}))

    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('index.html', nickname=user_info["nickname"], user_info=user_info , boardlist = boardList)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 2.로그인시 로그인 페이지로 넘어감
# 로그인 폼으로 렌더링, msg 파라미터를 같이 전달
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


# 3.로그인 서버
# 로그인 창, 로그인 성공,실패 알려줌, nickname receive는 사용여부에 따라 삭제가능. 있어도 상관없음. 토큰유지 2시간
@app.route('/api/login', methods=['POST'])
def sign_in():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    # nick_receive = request.form['nickname_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.datetime.utcnow() + timedelta(seconds=60 * 60 * 2)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 4. 회원가입 서버
# 회원가입 api /회원 정보를 받아 비밀번호를 해쉬 처리하여 db에 저장
@app.route('/api/register', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    nick_receive = request.form['nickname_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "nickname": nick_receive,  # 프로필 기본값=닉네임----------원래는 id
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


# 5. 아이디 중복확인
@app.route('/api/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# 6. 닉네임 중복확인
@app.route('/api/check_nick', methods=['POST'])
def check_nick():
    nick_receive = request.form['nickname_give']
    exists = bool(db.users.find_one({"nick": nick_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# ------------------------------------------------여기까지가 로그인 관련 -------------------------------------------

# ------------------------------------------------HTML 렌더링 ---------------------------------------------------

# header 부분 리뷰 작성 버튼 클릭 시 작성폼으로 렌더링
@app.route('/writeForm/<nickname>')
def write(nickname):
    token_receive = request.cookies.get('mytoken')
    try:
        # 쿠키에 있는 유저의 정보를 읽어옴
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # 읽어온 유저의 id를 통해서 db에서 나머지 정보 찾기
        user_info = db.users.find_one({"username": payload["id"]})

        status = False

        return render_template('writeForm.html', user_info=user_info, status=status)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 단일객체 렌더링
@app.route('/ObjectView/<num>')
def view(num):


    token_receive = request.cookies.get('mytoken')
    try:
        # 쿠키에 있는 유저의 정보를 읽어옴
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # 읽어온 유저의 id를 통해서 db에서 나머지 정보 찾기
        user_info = db.users.find_one({"username": payload["id"]})

        # board db에서 해당 num값에 해당하는 dic 찾아오기
        post = db.board.find_one({'num': num}, {'_id': False})

        # 쿠키에 있는 유저의 아이디와 board에 있는 게시물의 id가 같으면 Ture
        status = post["nickname"] == user_info['nickname']


        return render_template('ObjectView.html', user_info=user_info, post=post, num=num, status=status )

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 회원가입 폼으로 렌더링,
@app.route('/register')
def register():
    return render_template('register.html')



#------------------------------------------------기능구현 API ---------------------------------------------------

# 전체 후기 조회 /Get방식 메서드를 이용 새로고침 시 전체목록을 가져온다.
# DB에 더미데이터 집어넣어서 확인하기
#@app.route("/boardList", methods=["GET"])
#def board_list():
#    boardList = list(db.board.find({}, {'_id': False}))

#    return jsonify({'boardlist': boardList})




# 작성 후 DB에 저장
@app.route('/write', methods=['POST'])
def insert_content():

    #현재 시간을 primary 키값으로 설정
    num = request.form["num_give"]

    # 파라미터값 받기
    file = request.files["file_give"]
    title_receive = request.form['title_give']
    content_receive = request.form['content_give']
    nickname_receive = request.form['nickname_give']
    extension = file.filename.split('.')[-1]

    today = datetime.datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    filename = f'file-{mytime}'

    save_to = f'static/userImg/{filename}.{extension}'
    file.save(save_to)

    doc = {
        'num': num,
        'title': title_receive,
        'nickname': nickname_receive,
        'content': content_receive,
        'file': f'{filename}.{extension}'

    }
    print(doc)

    db.board.insert_one(doc)

    return jsonify({'msg': "작성완료!", 'num': num})


# 포스트 삭제
@app.route('/api/delete_post', methods=['POST'])
def delete_word():
    num_receive = request.form["num_give"]
    db.board.delete_one({"num": int(num_receive)})
    return jsonify({'result': 'success', 'msg': '포스트 삭제ㅠ'})


# 포스트 수정
@app.route('/api/update_post/<num>')
def update_post(num):
    token_receive = request.cookies.get('mytoken')
    try:
        # 쿠키에 있는 유저의 정보를 읽어옴
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # 읽어온 유저의 id를 통해서 db에서 나머지 정보 찾기
        user_info = db.users.find_one({"username": payload["id"]})

        # board db에서 해당 num값에 해당하는 dic 찾아오기
        post = db.board.find_one({'num': num}, {'_id': False})
        print(post)
        status = True

        return render_template('writeForm.html', user_info=user_info, status=status, post=post)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# 상세페이지에서 수정 버튼 클릭 시 -> JWT토큰 이용 , 사용자 정보를 WRITE 폼으로 보내어서 수정한다.
@app.route('/write/update', methods=['POST'])
def update_content():
    # 파라미터값 받기

    file = request.files["file_give"]
    title_receive = request.form['title_give']
    content_receive = request.form['content_give']
    nickname_receive = request.form['nickname_give']
    num_receive = request.form['num_give']

    num = num_receive

    extension = file.filename.split('.')[-1]

    today = datetime.datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    filename = f'file-{mytime}'

    save_to = f'static/userImg/{filename}.{extension}'
    file.save(save_to)

    
    db.board.update_one(
        {'num': num},
        {'$set': {
            'title': title_receive,
            'nickname': nickname_receive,
            'content': content_receive,
            'file': f'{filename}.{extension}'}
        }
    )

    return jsonify({'msg': "수정완료!", 'num': num})





if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
