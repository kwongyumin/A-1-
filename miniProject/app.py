from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from datetime import datetime

from pymongo import MongoClient
client = MongoClient("mongodb+srv://test:sparta@cluster0.u3t9k.mongodb.net/Cluster0?retryWrites=true&w=majority")
db = client.miniProject

# db컬렉션은 회원정보를 담을 users
# 게시판 정보를 담을 board 를 사용!

#로그인-> JWT토큰 -> 세션 유지 가능!

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


#최상위 수정필요
@app.route('/')
def login():
    return render_template('login.html')

#메인
@app.route('/main')
def main():
    return render_template('index.html')

#작성
@app.route('/writeForm')
def write():
    return render_template('writeForm.html')

#단일객체 뷰
@app.route('/ObjectView')
def view():
    return render_template('ObjectView.html')


#로그인 /회원가입 API
@app.route('/sign_in')
def sign():
    msg = request.args.get("msg");
    return render_template('login.html',msg=msg)










# 전체 후기 조회 /Get방식 메서드를 이용 새로고침 시 전체목록을 가져온다.
# DB에 더미데이터 집어넣어서 확인하기
@app.route("/boardList", methods=["GET"])
def board_list():

    boardList = list(db.board.find({}, {'_id': False}))

    return jsonify({'boardlist': boardList})

#작성란 -> 내용들을 DB에 저장!

@app.route('/write', methods=['POST'])
def insert_content():

    # 넘버링
    count = list(db.board.find({}, {'_id': False}))
    num = len(count) + 1

    #파라미터값 받기
    title_receive = request.form['title_give']
    content_receive = request.form['content_give']
    file = request.files["file_give"]

    extension = file.filename.split('.')[-1]

    today = datetime.now()
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


# 객체마다 부여된 num값을 받아와서 url에 합쳐서 view 쪽에서 받아준다.(ex: window.location.href="/view?num="+num)
@app.route("/getTitleNum",methods=["POST"])
def select_num():



    return jsonify({"":""})

#단일 객체의 num값을 받은 view 페이지에서는 num값을 사용해서
#num값에 해당하는 객체의 정보를 받는다. (url로 넘겨받은 num값을 활용 / let getLink = window.location.search)
#split 함수를 사용 필요한 부분만 사용,

@app.route("/getTitleNumView",methods=["POST"])
def get_num_view():


    return jsonify({"":""})





if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)