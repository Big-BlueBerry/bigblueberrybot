from flask import Flask, Response, jsonify, request
from datetime import date
import urllib.request
import json
import dms
import os
from slacker import Slacker
app = Flask(__name__)

slack = Slacker(os.environ.get('SLACK_TOKEN'))
VERIFICATION_TOKEN = os.environ.get('VERIFICATION_TOKEN')

members_info = {}

with open('memberinfo.txt', 'w+') as f:
    for l in f.readlines():
        ID, _id, pw = l.split(' ')
        members_info[ID] = _id, pw

def set_userinfo(user_id, _id, pw):
    members_info[user_id] = _id, pw
    with open('memberinfo.txt', 'a') as f:
        f.write(f'{user_id} {_id} {pw}\n')

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
        return Response(json.dumps(msg), mimetype='application/json')
    print(f'토큰이 다름!!\n받은거: {request.form.get("token")}\n예상한거: {VERIFICATION_TOKEN}')

@app.route('/slack/command/meal', methods=['POST'])
def meal():
    print(request.form.get('text'))
    try:
        res = dms.meal(date.today())
    except Exception as e:
        print('err', e.args)
        msg = {'response_type': 'in_channel', 'text': f'에러:blush::gun:\n{e.args[0]}'}
        return Response(json.dumps(msg), mimetype='application/json')
    return Response(res, mimetype='application/json')

@app.route('/slack/command/login', methods=['POST'])
def login():
    form = json.loads(request.form['payload'])
    text = form['text']
    if text.count(' ') != 1:
        msg = {
            "text": "사용법: /로그인 아이디 비밀번호 (아이디와 비밀번호에 공백 없어야함)"
        }
        return Response(json.dumps(msg), mimetype='application/json')
    _id, pw = text.split(' ')
    try:
        s = dms.login(_id, pw)
    except Exception as ex:
        msg = {"text": ex.args[0]}
        return Response(json.dumps(msg), mimetype='application/json')
    set_userinfo(form['user']['id'], _id, pw)
    msg = {"text": "로그인 되었음 굳굳"}
    
    return Response(json.dumps(msg), mimetype='application/json')

@app.route('/slack/command/home', methods=['POST'])
def janryu():
    pass

@app.route('/slack/command/more', methods=['POST'])
def more():
    pass

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
