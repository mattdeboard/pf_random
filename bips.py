import httplib2
import urllib
import re
from BeautifulSoup import *
from random import randrange


http = httplib2.Http()

def login():
        ''' This performs the authentication operation, then returns a dictionary
        with the cookie back to post() '''
        
        url = 'http://postfarm.net/login.php'
        body = {'do':'login',
                'url':'/login.php',
                'vb_login_md5password':pw_hash, # hashed password pulled from login.php,
                'vb_login_md5password_utf':utf_pw_hash, # hashed password pulled from login.php,
                's':'',
                'securitytoken':'guest',
                'vb_login_username':username, # username string,
                'vb_login_password':'' # remains empty; this is a field for clear text password,
                'cookieuser':'1'}
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        
        response, content = http.request(url, 'POST', headers=headers, body=urllib.urlencode(body))
        ''' Check for bad/changed/invalid passwords. This thing still needs work. '''
        failedLogin = re.search('invalid username', content)
        if failedLogin:
                raise Exception('Invalid username/password.')
        
        headers['Cookie'] = response['set-cookie']

        return headers
        
def random_url(thread_ids):
        ''' Selects a random thread id from selection of ids passed in from post().
        Then the thread id is concatenated with the static url. Both the
        random thread id and complete url are passed back to post(). '''
        
        threadurl = 'http://postfarm.net/showthread.php?t='
        generate_random_thread_id = thread_ids[randrange(0, len(thread_ids))]
        randurl = str(threadurl + generate_random_thread_id)
        return randurl, generate_random_thread_id


def post():
        headers = login()
        thread_ids = []
        searchurl = 'http://postfarm.net/search.php?do=getdaily'
        srchresp, srchcont = http.request(searchurl, 'GET', headers = headers)

        soup = BeautifulSoup(srchcont)
        td_list = soup.findAll('td', id=re.compile('td_threadtitle_\d+'))

        for td in td_list:
                id = td['id']
                match = re.match("td_threadtitle_(\d+)", id)
                thread_ids.append(match.group(1))

        randurl, rand_thread_id = random_url(thread_ids)

        page = BeautifulSoup(randurl)
        token_value = str(soup.find('input', attrs={'name':'securitytoken'})['value'])
        messagebody = {'message':'badass',
                       'fromquickreply':'1',
                       's':'',
                       'securitytoken':token_value,
                       'do':'postreply',
                       't':rand_thread_id,
                       'p':'who cares',
                       'parseurl':'1'}
        resp, cont = http.request(randurl, 'POST', headers=headers, body=urllib.urlencode(messagebody))
        print resp

if __name__ == '__main__':
        post()
        

