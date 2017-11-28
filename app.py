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
        return Response(msg, mimetype='application/json')
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
    msg = {
        "text": "DMS에 로그인할거냐?",
        "attachments": [
            {
                "text": "비밀번호를 평문으로 맡겨도 될 만큼 안전할 거 같냐?",
                "fallback": "안전할 거 같아?",
                "callback_id": "login_answer",
                "color": "#ff0000",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "answer",
                        "text": "네!!!",
                        "type": "button",
                        "style": "danger",
                        "value": "yes"
                    },
                    {
                        "name": "answer",
                        "text": "아뇨..",
                        "type": "button",
                        "value": "no"
                    }
                ]
            }
        ]
    }
    return Response(json.dumps(msg), mimetype='application/json')

@app.route('/slack/command/home', methods=['POST'])
def janryu():
    pass

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
