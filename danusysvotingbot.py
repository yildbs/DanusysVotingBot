# -*- coding: utf-8 -*-
 
import os
from flask import Flask, request, jsonify
import glob

import user
import voting as voting

try:
    os.mkdir('data') 
except:
    pass
app = Flask(__name__)
 
            
###################################
# Global variables
###################################
PASSWORD = ''
with open('__Password.txt', 'r', encoding='utf-8-sig') as f:
    for line in f.readlines():
        line = line.replace('\n','')
        line = line.replace('\r','')
        PASSWORD = line
        break

HELP = ""
HELP += "\n다누시스투표봇사용방법\n\n"
HELP += "'투표하기' : 투표하기\n"
HELP += "'관리자' : 관리자 명령어 확인\n"

ADMINHELP = ""
ADMINHELP += "\n다누시스투표봇 관리자 명령어\n\n"
ADMINHELP += "'관리자' : 관리자 명령어 확인\n"
ADMINHELP += "'투표결과' : 투표 결과 확인\n"
ADMINHELP += "'투표결과삭제진짜진짜123' : 투표 결과 제거, 사용시 주의\n"
ADMINHELP += "'사용자제거' : 이름을 잘못 등록했거나 할때 사용자 제거\n"

USERS = user.Users()
USERS.loadfromdata()

ARTICLES = {}
ARTICLENAMES = []
for articlename in glob.glob('___*'):
    articlename = articlename.replace('___', '')
    ARTICLENAMES += [articlename]

    article = voting.VotingArticle(articlename)
    ARTICLES[articlename] = article

# Groups
GROUPS = {}
with open('__Groups.txt', 'r', encoding='utf-8-sig') as f:
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


@app.route('/keyboard')
def Keyboard():
    dataSend = {
        "type" : "buttons",
        "buttons" : ["시작"]
    }
    return jsonify(dataSend)


@app.route('/message', methods=['POST'])
def Message():
    global HELP
    global ADMINHELP
    global USERS
    global PASSWORD
    global ARTICLES
    global ARTICLENAMES
    global GROUPS

    dataReceive = request.get_json()

    content = dataReceive['content']
    user_key = dataReceive['user_key']

    print(dataReceive)

    ###############################
    #### STATE 설정
    ###############################
    if USERS.find(user_key):
        state = USERS.getuserstate(user_key)
        if content == "시작":
            state = 'DEFAULT'
        if USERS.getusername(user_key) == '':
            state = 'MYNAME'
    else:
        state = 'ENROLL'

    ###############################
    #### FSM DEFAULT : 기본 메뉴
    ###############################
    if state == 'DEFAULT':
        if content == "시작":
            USERS.setuserstate(user_key, 'DEFAULT')
            text = ""
            dataSend = {
                "message": {
                    "text": "안녕하세요. "+ USERS.getusername(user_key) + "님" + HELP
                }
            }
        elif content == "투표하기":
            USERS.setuserstate(user_key, 'SELECTARTICLE')
            text = ""
            text += "투표할 항목을 입력해주세요\r\n"
            text += "------------\r\n"
            for articlename in ARTICLENAMES:
                text += articlename + '\r\n'
            text += "------------\r\n"
            dataSend = {
                "message": {
                    "text": text
                }
            }
        elif content == "관리자":
            USERS.setuserstate(user_key, 'PASSWORD')
            USERS.setuserstateadmin(user_key, 'ADMINHELP')
            dataSend = {
                "message": {
                    "text": "관리자전용: 비밀번호를 입력해주세요."
                }
            }    
        elif content == "투표결과":
            USERS.setuserstate(user_key, 'PASSWORD')
            USERS.setuserstateadmin(user_key, 'RESULT')
            dataSend = {
                "message": {
                    "text": "관리자전용: 비밀번호를 입력해주세요."
                }
            }
        elif content == "투표결과삭제진짜진짜123":
            USERS.setuserstate(user_key, 'PASSWORD')
            USERS.setuserstateadmin(user_key, 'DELETERESULT')
            dataSend = {
                "message": {
                    "text": "관리자전용: 비밀번호를 입력해주세요."
                }
            }
        elif content == "사용자제거":
            USERS.setuserstate(user_key, 'PASSWORD')
            USERS.setuserstateadmin(user_key, 'DELETEUSER')
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
    #### FSM SELECTARTICLE : 투표할 항목 선택
    ###############################
    elif state == 'SELECTARTICLE':
        currentusername = USERS.getusername(user_key)

        if content in ARTICLENAMES:
            USERS.setuserstate(user_key, 'VOTING')
            USERS.setuserstatevoting(user_key, content)

            dataSend = {
                "message": {
                    "text": "투표해주세요\r\n" + ARTICLES[content].getreason()
                }
            }
        else:
            USERS.setuserstate(user_key, 'DEFAULT')
            dataSend = {
                "message": {
                    "text": content + "는 항목에 없습니다. 처음으로 되돌아 갑니다. \n"
                }
            }

    ###############################
    #### FSM VOTING 투표하기
    ###############################
    elif state == 'VOTING':
        articlename = USERS.getuserstatevoting(user_key)
        user_name = USERS.getusername(user_key)

        ret = ARTICLES[articlename].uservoteto(user_key, user_name, content)
        if ret == 'SUCCESS':
            USERS.setuserstate(user_key, 'DEFAULT')
            dataSend = {
                "message": {
                    "text": "당신은 " + content + " 를 뽑았습니다!\n" + HELP
                }
            }
        elif ret == 'NOTINCANDIDATES':
            dataSend = {
                "message": {
                    "text": content + "는 후보 중에 없습니다. 다시 입력해주세요\n"
                }
            }
        elif ret == 'CANNOTVOTETOYOURTEAM':
            dataSend = {
                "message": {
                    "text": "같은 부서 직원에게 투표 할 수 없습니다! 다시 투표해주세요\n"
                }
            }
            
    ###############################
    #### FSM PASSWORD: 암호 입력 및 투표 현황 출력 
    ###############################
    elif state == 'PASSWORD':
        USERS.setuserstate(user_key, 'DEFAULT')
        if content == PASSWORD:
            if USERS.getuserstateadmin(user_key) == 'ADMINHELP':
                dataSend = {
                    "message": {
                        "text": ADMINHELP
                    }
                }        
            elif USERS.getuserstateadmin(user_key) == 'RESULT':
                summary = ''
                for articlename in ARTICLENAMES:
                    summary += ARTICLES[articlename].getvotingsummary(USERS)
                
                dataSend = {
                    "message": {
                        "text": summary
                    }
                }
            elif USERS.getuserstateadmin(user_key) == 'DELETERESULT':
                summary = ''
                for articlename in ARTICLENAMES:
                    summary += ARTICLES[articlename].getvotingsummary(USERS)
                summary += "\n\n투표결과 삭제되었습니다\n"
				
                for articlename in ARTICLENAMES:
                    ARTICLES[articlename].deleteuser(user_key)
                dataSend = {
                    "message": {
                        "text": summary
                    }
                }
            elif USERS.getuserstateadmin(user_key) == 'DELETEUSER':
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
        USERS.setuserstateadmin(user_key, 'DEFAULT')

    ###############################
    #### FSM DELETEUSER: 유저 제거
    ###############################
    elif state == 'DELETEUSER':
        message = ''
        if USERS.deleteuser(content):
            message += content + ' 제거 되었습니다'
        else:
            message += content + ' 제거 되지 않았습니다'
        for articlename in ARTICLENAMES:
            ARTICLES[articlename].deleteuser(user_key)
        
        USERS.setuserstate(user_key, 'DEFAULT')
        USERS.setuserstateadmin(user_key, 'DEFAULT')
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
