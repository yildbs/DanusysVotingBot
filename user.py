import os
import glob


class User:
    def __init__(self, user_key):
        self.user_key = user_key
        self.name = ''
        self.state = 'DEFAULT'
        self.stateadmin = 'DEFAULT'
        self.statevoting = 'DEFAULT'
        self.modified = False
        
    def save(self):
        if self.modified:
            with open('data/'+self.user_key, 'w', encoding='utf-8-sig') as f:
                f.write(self.user_key+','+self.name+','+self.state+','+self.stateadmin)
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
            with open(filename, 'r', encoding='utf-8-sig') as f:
                line = f.read()
                line = line.replace('\n', '')
                user_key, name, state, stateadmin = line.split(',')
                self.adduser(user_key)
                self.setusername(user_key, name)

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
        print(user_key)
        print(self.users)
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

    def getuserstateadmin(self, user_key):
        try:
            return self.users[user_key].stateadmin
        except:
            return 'NOEXISTINGUSER'
            
    def setuserstateadmin(self, user_key, stateadmin):
        try:
            self.users[user_key].stateadmin = stateadmin
            self.users[user_key].modified = True
        except:
            return 'NOEXISTINGUSER'        

    def getuserstatevoting(self, user_key):
        try:
            return self.users[user_key].statevoting
        except:
            return 'NOEXISTINGUSER'
            
    def setuserstatevoting(self, user_key, statevoting):
        try:
            self.users[user_key].statevoting = statevoting
            self.users[user_key].modified = True
        except:
            return 'NOEXISTINGUSER'        
    