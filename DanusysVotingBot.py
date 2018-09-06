# -*- coding: utf-8 -*-
 
import os
from flask import Flask, request, jsonify
import glob

try:
    os.mkdir('data') 
except:
    pass
app = Flask(__name__)
 
@app.route('/keyboard')
def Keyboard():
    dataSend = {
        "type" : "buttons",
        "buttons" : ["시작"]
    }
    return jsonify(dataSend)

class User:
    def __init__(self, user_key):
        self.user_key = user_key
        self.name = ''
        self.voteto = ''
        self.state = 'DEFAULT'
        self.adminstate = 'DEFAULT'
        self.modified = False
        
    def save(self):
        if self.modified:
            with open('data/'+self.user_key, 'w', encoding='UTF8') as f:
                f.write(self.user_key+','+self.name+','+self.state+','+self.adminstate+','+self.voteto)
            self.modified = False

class Users:
    def __init__(self):
        self.users = {}
    
    def save(self, user_key):
        try:
            self.users[user_key].save()
        except:
            pass
    
    def loadfromdata(self):
        for filename in glob.glob('data/*'):
            with open(filename, 'r', encoding='UTF8') as f:
                line = f.read()
                line = line.replace('\n', '')
                user_key, name, state, adminstate, voteto = line.split(',')
                self.adduser(user_key)
                self.setusername(user_key, name)
                self.setuservoteto(user_key, voteto)

    def deleteuser(self, name):
        deleted = False
        if self.findbyname(name):
            for user_key, user in self.users.items():
                if name == user.name:
                    deleted = True
                    self.users.pop(user_key)
                    try:
                        os.remove('data/'+user_key)
                    except:
                        pass
                    break
        return deleted
                
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

    def adduser(self, user_key):
        self.users[user_key] = User(user_key)
        self.users[user_key].modified = True

    def setusername(self, user_key, name):
        self.users[user_key].name = name
        self.users[user_key].modified = True
        
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
            self.users[user_key].modified = True
        except:
            return 'NOEXISTINGUSER'

    def getuseradminstate(self, user_key):
        try:
            return self.users[user_key].adminstate
        except:
            return 'NOEXISTINGUSER'
            
    def setuseradminstate(self, user_key, adminstate):
        try:
            self.users[user_key].adminstate = adminstate
            self.users[user_key].modified = True
        except:
            return 'NOEXISTINGUSER'        
    
    def setuservoteto(self, user_key, excellent):
        self.users[user_key].voteto = excellent
        self.users[user_key].modified = True
        
    def getuservoteto(self, user_key):
        return self.users[user_key].voteto
    
    def deletevotingresults(self):
        for user_key, user in self.users.items():
            user.voteto = ''

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
            text2 += voteto + ' - ' + str(num) + '표\n'
        return text2 + "\n\n" + text + "\n"


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

for candidate in CANDIDATES:
	GROUPS[candidate] = 'CANDIDATES'

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
HELP += "\n다누시스투표봇사용방법\n\n"
HELP += "'투표하기' : 투표하기\n\n"
HELP += "'관리자' : 관리자 명령어 확인\n"

ADMINHELP = ""
ADMINHELP += "\n다누시스투표봇 관리자 명령어\n\n"
ADMINHELP += "'관리자' : 관리자 명령어 확인\n"
ADMINHELP += "'투표결과' : 투표 결과 확인\n"
ADMINHELP += "'투표결과삭제진짜진짜123' : 투표 결과 제거, 사용시 주의\n"
ADMINHELP += "'사용자제거' : 이름을 잘못 등록했거나 할때 사용자 제거\n"

#ADMINHELP += "'결과제거' : 투표 결과 제거\n"

USERS = Users()
USERS.loadfromdata()

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
        elif content == u"투표하기":
            USERS.setuserstate(user_key, 'VOTING')
            text = ""
            dataSend = {
                "message": {
                    "text": "투표해주세요." + REASON
                }
            }
        elif content == u"관리자":
            USERS.setuserstate(user_key, 'PASSWORD')
            USERS.setuseradminstate(user_key, 'ADMINHELP')
            dataSend = {
                "message": {
                    "text": "관리자전용: 비밀번호를 입력해주세요."
                }
            }    
        elif content == u"투표결과":
            USERS.setuserstate(user_key, 'PASSWORD')
            USERS.setuseradminstate(user_key, 'RESULT')
            dataSend = {
                "message": {
                    "text": "관리자전용: 비밀번호를 입력해주세요."
                }
            }
        elif content == u"투표결과삭제진짜진짜123":
            USERS.setuserstate(user_key, 'PASSWORD')
            USERS.setuseradminstate(user_key, 'DELETERESULT')
            dataSend = {
                "message": {
                    "text": "관리자전용: 비밀번호를 입력해주세요."
                }
            }
        elif content == u"사용자제거":
            USERS.setuserstate(user_key, 'PASSWORD')
            USERS.setuseradminstate(user_key, 'DELETEUSER')
            dataSend = {
                "message": {
                    "text": "관리자전용: 비밀번호를 입력해주세요."
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
    #### FSM VOTING : 투표하기
    ###############################
    elif state == 'VOTING':
        currentusername = USERS.getusername(user_key)

        if content not in CANDIDATES:
            dataSend = {
                "message": {
                    "text": content + "는 후보 중에 없습니다. 다시 입력해주세요\n"
                }
            }
        elif GROUPS[currentusername] == GROUPS[content]:
            dataSend = {
                "message": {
                    "text": "같은 부서 직원에게 투표 할 수 없습니다! 다시 투표해주세요\n"
                }
            }
        else:
            USERS.setuserstate(user_key, 'DEFAULT')
            USERS.setuservoteto(user_key, content)
            dataSend = {
                "message": {
                    "text": "당신은 " + content + " 를 뽑았습니다!\n" + HELP
                }
            }

    ###############################
    #### FSM PASSWORD: 암호 입력 및 투표 현황 출력 
    ###############################
    elif state == 'PASSWORD':
        USERS.setuserstate(user_key, 'DEFAULT')
        if content == PASSWORD:
            if USERS.getuseradminstate(user_key) == 'ADMINHELP':
                dataSend = {
                    "message": {
                        "text": ADMINHELP
                    }
                }        
            elif USERS.getuseradminstate(user_key) == 'RESULT':
                summary = USERS.getvotingsummary()
                dataSend = {
                    "message": {
                        "text": summary
                    }
                }
            elif USERS.getuseradminstate(user_key) == 'DELETERESULT':
                summary = USERS.getvotingsummary()
                summary += "\n\n투표결과 삭제되었습니다\n"
                USERS.deletevotingresults()
                dataSend = {
                    "message": {
                        "text": summary
                    }
                }
            elif USERS.getuseradminstate(user_key) == 'DELETEUSER':
                USERS.setuserstate(user_key, 'DELETEUSER')
                dataSend = {
                    "message": {
                        "text": "제거할 사람의 이름을 입력하세요\n"
                    }
                }    
        else:
            dataSend = {
                "message": {
                    "text": "비밀번호가 틀렸습니다. 처음으로 되돌아 갑니다. " + HELP
                }
            }
        USERS.setuseradminstate(user_key, 'DEFAULT')

    ###############################
    #### FSM DELETEUSER: 유저 제거
    ###############################
    elif state == 'DELETEUSER':
        message = ''
        if USERS.deleteuser(content):
            message += content + ' 제거 되었습니다'
        else:
            message += content + ' 제거 되지 않았습니다'
        USERS.setuserstate(user_key, 'DEFAULT')
        USERS.setuseradminstate(user_key, 'DEFAULT')
        dataSend = {
            "message": {
                "text": message
            }
        }        
        
    ###############################
    #### FSM ENROLL: 신규 가입 메시지 출력
    ###############################
    elif state == 'ENROLL':
        USERS.adduser(user_key)
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
            USERS.adduser(user_key)
            USERS.setusername(user_key, content)
            USERS.setuserstate(user_key, 'DEFAULT')
            dataSend = {
                "message": {
                    "text": "당신의 이름은 " + content + " 입니다!" + HELP
                }
            }
    
    USERS.save(user_key)
    
    return jsonify(dataSend)
 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 6000)
