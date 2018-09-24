import os
import glob 


class VotingArticle:
    def __init__(self, votingname):
        self.result = {}
        self.votingname = votingname
        self.votingnamedir = '___'+votingname

        # Reason
        reason = ''
        with open(self.votingnamedir + '/__Reason.txt', 'r', encoding='utf-8-sig') as f:
            reason += f.read()
        self.reason = reason

        # Candidates
        candidates = []
        with open(self.votingnamedir + '/__Candidates.txt', 'r', encoding='utf-8-sig') as f:
            for line in f.readlines():
                line = line.replace('\n','')
                line = line.replace('\r','')
                if line != '':
                    candidates.append(line)
        self.candidates = candidates

        # Groups
        groups = {}
        for candidate in candidates:
            groups[candidate] = 'CANDIDATES'
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
                    groups[line] = groupname
        self.groups = groups
        
        self.loadfromdata()

    def uservoteto(self, user_key, user_name, voteto):
        if voteto not in self.candidates:
            return 'NOTINCANDIDATES'
        elif self.groups[user_name] == self.groups[voteto]:
            return 'CANNOTVOTETOYOURTEAM'

        self.result[user_key] = voteto
        self.save(user_key, voteto)
        return 'SUCCESS'

    def getvotingname(self):
        return self.votingname

    def getreason(self):
        return self.reason
        
    def save(self, user_key, voteto):
        try:
            os.mkdir(self.votingnamedir + '/data') 
        except:
            pass
    
        with open(self.votingnamedir + '/data/'+user_key, 'w', encoding='utf-8-sig') as f:
            f.write(voteto)
            
    def deleteuser(self, user_key):
        try:
            os.remove(self.votingnamedir + '/data/'+user_key)
            self.result.pop(user_key, None)
        except:
            pass
            
    def loadfromdata(self):
        for filename in glob.glob(self.votingnamedir + '/data/*'):
            user_key = filename[max(filename.rfind('/'), filename.rfind('\\'))+1:]
            with open(filename, 'r', encoding='utf-8-sig') as f:
                line = f.read()
                voteto = line.replace('\n', '')
                self.result[user_key] = voteto

    def getvotingsummary(self, users):
        counting = {}
        text1 = ""
        for user_key, voteto in self.result.items():
            name = users.getusername(user_key)
            text1 += name + ' --> ' + voteto + '\n'
            if voteto != '':
                if voteto not in counting:
                    counting[voteto] = 1
                else:
                    counting[voteto] += 1            
        text2 = ""
        for voteto, num in counting.items():
            text2 += voteto + ' - ' + str(num) + '표\n'
        text = "----------\r\n"
        text += self.votingname + '\r\n'
        text += text2 + '\r\n\r\n'
        text += text1 + '\r\n'    
        return text