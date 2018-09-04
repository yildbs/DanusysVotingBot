# -*- coding: utf-8 -*-
 
import os
from flask import Flask, request, jsonify
 
app = Flask(__name__)
 
@app.route('/keyboard')
def Keyboard():
    dataSend = {
        "type" : "buttons",
        "buttons" : ["시작"]
    }
    return jsonify(dataSend)

class User:
    def __init__(self, user_key, name):
        self.user_key = user_key
        self.name = name
        self.state = 'DEFAULT'
        self.voteto = ''

class Users:
    def __init__(self):
        self.users = {}

    def find(self, user_key):
        for _, user in self.users.items():
            if user_key == user.user_key:
                return True
        return False

    def findbyname(self, name):
        for _, user in self.users.items():
            if name == user.name:
                return True
        return False

    def adduser(self, user_key, name):
        self.users[user_key] = User(user_key, name)

    def getusername(self, user_key):
        try:
            return self.users[user_key].name
        except:
            return 'NOEXISTINGUSER'

    def getuserstate(self, user_key):
        try:
            return self.users[user_key].state
        except:
            return 'NOEXISTINGUSER'

    def setuserstate(self, user_key, state):
        try:
            self.users[user_key].state = state
        except:
            return 'NOEXISTINGUSER'

    def setuservoteto(self, user_key, excellent):
        self.users[user_key].voteto = excellent
        
    def getuservoteto(self, user_key):
        return self.users[user_key].voteto

    def getvotingsummary(self):
        counting = {}
        text = ""
        for user_key, user in self.users.items():
            name = user.name
            voteto = user.voteto
            text += name + ' --> ' + voteto + '\n'
            if voteto != '':
                if voteto not in counting:
                    counting[voteto] = 1
                else:
                    counting[voteto] += 1
        text2 = ""
        for voteto, num in counting.items():
            text2 += voteto + ' - ' + str(num) + '표'
        return text2 + "\n" + text + "\n"


REASON = "\n\n"
with open('__Reason.txt', 'r', encoding='UTF8') as f:
    REASON += f.read()
    REASON = REASON.replace('\n\n', '\n')


CANDIDATES = []
with open('__Candidates.txt', 'r', encoding='UTF8') as f:
    for line in f.readlines():
        line = line.replace('\n','')
        line = line.replace('\r','')
        CANDIDATES.append(line)


GROUPS = {}
with open('__Groups.txt', 'r', encoding='UTF8') as f:
    groupname = '' 
    for line in f.readlines():
        line = line.replace('\n','')
        line = line.replace('\r','')
        line = line.replace(' ','')

        if line == '':
            continue
        elif line.startswith('Group'):
            groupname = line
        else:
            GROUPS[line] = groupname

            
PASSWORD = ''
with open('__Password.txt', 'r', encoding='UTF8') as f:
    for line in f.readlines():
        line = line.replace('\n','')
        line = line.replace('\r','')
        PASSWORD = line
        break

#print(REASON)
#print(CANDIDATES)
#print(GROUPS)
#print(PASSWORD)

HELP = ""
HELP += "\n\n\n다누시스투표봇사용방법\n\n"
HELP += "'우수사원' : 우수사원 투표 시 입력\n"

USERS = Users()

@app.route('/message', methods=['POST'])
def Message():
    #global DB
    global REASON
    global CANDIDATES 
    global GROUPS
    global USERS
    global PASSWORD

    dataReceive = request.get_json()

    content = dataReceive['content']
    user_key = dataReceive['user_key']

    print(dataReceive)
    #print(user_key)

    ###############################
    #### state 설정
    ###############################
    if USERS.find(user_key):
        state = USERS.getuserstate(user_key)
        if content == u"시작":
            state = 'DEFAULT'
        if USERS.getusername(user_key) == '':
            state = 'MYNAME'
    else:
        state = 'ENROLL'

    ###############################
    #### FSM DEFAULT : 기본 메뉴
    ###############################
    if state == 'DEFAULT':
        if content == u"시작":
            USERS.setuserstate(user_key, 'DEFAULT')
            text = ""
            dataSend = {
                "message": {
                    "text": "안녕하세요. "+ USERS.getusername(user_key) + "님" + HELP
                }
            }
        elif content == u"우수사원":
            USERS.setuserstate(user_key, 'EXCELLENT')
            text = ""
            dataSend = {
                "message": {
                    "text": "투표할 우수사원의 이름을 입력해주세요." + REASON
                }
            }
        elif content == u"투표현황":
            USERS.setuserstate(user_key, 'PASSWORD')
            dataSend = {
                "message": {
                    "text": "관리자만 확인 할 수 있습니다. 관리자라면 비밀번호를 입력해주세요."
                }
            }
        else:
            USERS.setuserstate(user_key, 'DEFAULT')
            dataSend = {
                "message": {
                    "text": "오류!" + HELP
                }
            }
    ###############################
    #### FSM EXCELLENT : 우수사원 투표
    ###############################
    elif state == 'EXCELLENT':
        currentusername = USERS.getusername(user_key)

        if content not in CANDIDATES:
            dataSend = {
                "message": {
                    "text": content + "는 우수 사원 후보 중에 없습니다. '이름'만 다시 입력해주세요"
                }
            }
        elif GROUPS[currentusername] == GROUPS[content]:
            dataSend = {
                "message": {
                    "text": "같은 부서 직원에게 투표 할 수 없습니다! 다시 투표해주세요"
                }
            }
        else:
            USERS.setuserstate(user_key, 'DEFAULT')
            USERS.setuservoteto(user_key, content)
            dataSend = {
                "message": {
                    "text": "당신은 " + content + " 를 뽑았습니다!" + HELP
                }
            }

    ###############################
    #### FSM PASSWORD: 암호 입력 및 투표 현황 출력 
    ###############################
    elif state == 'PASSWORD':
        USERS.setuserstate(user_key, 'DEFAULT')
        if content == PASSWORD:
            summary = USERS.getvotingsummary()
            dataSend = {
                "message": {
                    "text": summary
                }
            }
        else:
            dataSend = {
                "message": {
                    "text": "비밀번호가 틀렸습니다. 처음으로 되돌아 갑니다. " + HELP
                }
            }
            
    ###############################
    #### FSM ENROLL: 신규 가입 메시지 출력
    ###############################
    elif state == 'ENROLL':
        USERS.adduser(user_key, '')
        USERS.setuserstate(user_key, 'MYNAME')
        dataSend = {
            "message": {
                "text": "본인의 이름을 입력해주세요!"
            }
        }

    ###############################
    #### FSM ENROLL: 이름 입력
    ###############################
    elif state == 'MYNAME':
        if content not in GROUPS:
            dataSend = {
                "message": {
                    "text": "잘못 입력하신것 같아요. 이름'만' 다시 입력해주세요"
                }
            }
        elif USERS.findbyname(content):
            dataSend = {
                "message": {
                    "text": "이미 존재하는 이름입니다. 본인의 이름을 입력해주세요."
                }
            }
        else:
            USERS.adduser(user_key, content)
            USERS.setuserstate(user_key, 'DEFAULT')
            dataSend = {
                "message": {
                    "text": "당신의 이름은 " + content + " 입니다!" + HELP
                }
            }
    return jsonify(dataSend)
 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 6000)
