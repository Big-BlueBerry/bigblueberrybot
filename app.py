from flask import Flask, Response, jsonify, request
from datetime import date
import urllib.request
import json
import dms
import os
import apscheduler
from slacker import Slackeㄴr
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()
app = Flask(__name__)

slack = Slacker(os.environ.get('SLACK_TOKEN'))
VERIFICATION_TOKEN = os.environ.get('VERIFICATION_TOKEN')

members_info = {}
auto_extend_members = {}

if not os.path.exists('memberinfo.txt'):
    open('memberinfo.txt', 'a').close()
if not os.path.exists('extendmembers.txt'):
    open('extendmembers.txt', 'a').close()
with open('memberinfo.txt', 'r+') as f:
    for l in f.readlines():
        ID, _id, pw = l.split(' ')
        members_info[ID] = _id, pw
        print('유저 로드: ', ID, _id, pw)

with open('extendmembers.txt', 'r+') as f:
    for l in f.readlines():
        ID, _class, seat = l.split(' ')
        auto_extend_members[ID] = _class, seat
        print('자동 연장 로드: ', ID, _class, seat)

def set_userinfo(user_id, _id, pw):
    members_info[user_id] = _id, pw
    with open('memberinfo.txt', 'a') as f:
        print('유저 저장: ', user_id, _id, pw)
        f.write(f'{user_id} {_id} {pw}\n')

def set_autoextend(user_id, _class, seat):
    auto_extend_members[user_id] = _class, seat
    with open('extendmembers.txt', 'a') as f:
        print('자동 연장 저장: ', user_id, _class, seat)
        f.write(f'{user_id} {_class} {seat}\n')

def remove_autoextend(user_id):
    auto_extend_members.pop(user_id, None)
    with open('extendmembers.txt', 'w+') as f:
        for ID in auto_extend_members.keys():
            _class, seat = auto_extend_members[ID]
            f.write(f'{ID} {_class} {seat}\n')

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=19)
def study_more_all_automembers():
    for user in auto_extend_members.keys():
        _class, seat = auto_extend_members[user]
        try:
            s = dms.login(*members_info[user])
        except Exception as ex:
            slack.chat.post_message(f"{user} 로그인 실패했음\n{ex.args[0]}")

        try:
            dms.study_more(s, _class, seat)
        except Exception as ex:
            slack.chat.post_message(f"{user} 연장 실패했음\n{ex.args[0]}")


def create_response(msg: dict):
    return Response(json.dumps(msg), mimetype='application/json')

@app.route('/')
def homepage():
    return """
    <h1>Hello heroku</h1>
    <p>It is currently {time}.</p>
    """.format(time=date.today())

@app.route('/slack/confirm', methods=['POST'])
def confirm():
    form = json.loads(request.form['payload'])
    print(form)
    if form.get('token') == VERIFICATION_TOKEN:
        chan = form.get('channel').get('name')
        answ = form.get('actions')[0].get('value') == 'yes'
        msg = {
            "text": '응 안전하지 않아~' if answ else '잘 아는군'
        }
        return create_response(msg)
    print(f'토큰이 다름!!\n받은거: {request.form.get("token")}\n예상한거: {VERIFICATION_TOKEN}')

@app.route('/slack/command/meal', methods=['POST'])
def meal():
    text = request.form.get('text')
    day = date.today()
    if text == '내일':
        day = day + date.replace(day=day.day+1)
    try:
        res = dms.meal(day)
    except Exception as e:
        print('err', e.args)
        msg = {'response_type': 'in_channel', 'text': f'에러:blush::gun:\n{e.args[0]}'}
        return create_response(msg)
    return create_response(res)

@app.route('/slack/command/login', methods=['POST'])
def login():
    form = request.form
    print(form)
    text = form['text']
    if text.count(' ') != 1:
        msg = {
            "text": "사용법: /로그인 아이디 비밀번호 (아이디와 비밀번호에 공백 없어야함)"
        }
        return create_response(msg)
    _id, pw = text.split(' ')
    print(f'{form["user_name"]} 한테서 아이디 {_id} 비번 {pw} 받음')
    try:
        s = dms.login(_id, pw)
    except Exception as ex:
        print('로그인중 에러', ex)
        msg = {"text": ex.args[0]}
        return create_response(msg)
    set_userinfo(form['user_id'], _id, pw)
    msg = {"text": "로그인 되었음 굳굳"}
    print(f'{form["user_name"]} 로그인 성공')
    return create_response(msg)

@app.route('/slack/command/home', methods=['POST'])
def janryu():
    pass

@app.route('/slack/command/more', methods=['POST'])
def more():
    print(request.form)
    form = request.form
    text = form['text']

    if text == '취소':
        try:
            dms.cancle_more(dms.login(*members_info[form['user_id']]))
        except Exception as ex:
            msg = {"text": ex.args[0]}
            return create_response(msg)
        msg = {"text": "취소했음"}
        return create_response(msg)

    elif text == '자동 취소':
        remove_autoextend(form['user_id'])
        msg = {"text": "너의 자동 연장이 취소됐다"}
        return create_response(msg)

    user = form['user_id']
    if text.count(' ') == 1 and text != ' ':
        _class, seat = text.split(' ')
    elif text.count(' ') == 2:
        _class, seat, auto = text.aplit(' ')
        if auto == '자동':
            set_autoextend(user, _class, seat)
            msg = {"text": "너의 자동 연장이 등록되었다"}
            return create_response(msg)
    else:
        msg = {
            'text': '사용법: `/연장 (교실) (자리)` 으로 연장 신청\n`/연장 (교실) (자리) 자동` 으로 자동연장 신청\n`/연장 자동 취소` 로 자동연장 취소\n`/연장 취소` 로 연장 취소'
        }
        return create_response(msg)
    session = dms.login(*members_info[user])
    try:
        dms.study_more(session, _class, seat)
    except Exception as ex:
        print('연장 신청중 에러', ex.args)
        msg = {"text": ex.args[0]}
        return create_response(msg)

    msg = {"text": "성공적으로 신청되었음!"}
    return create_response(msg)

if __name__ == '__main__':
    sched.start()
    app.run(debug=True, use_reloader=True)
