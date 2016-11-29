import mechanicalsoup
import pathlib
import lxml
from bs4 import BeautifulSoup
import pprint
import json

baseURL = 'https://cams.floridapoly.org/Student/'
classDataList = {}

def getPage(browser, fileName):
    try:
        page = browser.get(baseURL + fileName)
    except:
        page = type('obj', (object,), {'content': '', 'soup': ''})
        page.content = open('_cache/' + fileName + '.html', 'r').read()
        page.soup = BeautifulSoup(page.content, 'lxml')
    return page

def postPage(browser, fileName, params):
    try:
        page = browser.post(baseURL + fileName, params)
    except:
        try:
            addToURL = params[u'page']
        except KeyError:
            addToURL = ''
        page = type('obj', (object,), {'content': '', 'soup': ''})
        url = '_cache/' + fileName + addToURL + '.html'
        page.content = open(url, 'r').read()
        page.soup = BeautifulSoup(page.content, 'lxml')
    return page

def timeObjFromStr(string):
    hour = int(string.split(':')[0])
    minute = int(string.split(':')[1].split(':')[0])
    pm = (string[-2:] == "PM")
    if pm:
        hour += 12
        if hour == 24 or hour == 12:
            hour -= 12
    # return type('obj', (object,), {'h': hour, 'm': minute})
    return {'h': hour, 'm': minute}

def to2Str(integer):
    if integer < 10:
        return '0' + str(integer)
    else:
        return str(integer)

def getClassesFromPage(page):
    soup = page.soup
    classes = soup.select('tr.courseInfo')
    for theClass in classes:
        # course number; solely for identification purposes
        a = theClass.find_all('td') # tds containing course info
        b = str(a[0].contents[0]).strip() # number + section number
        section = b[-2:]
        number = b[:-2]

        # professors = []
        # rooms = []

        # get a list of meeting times
        try:
            meetingsTable = theClass.parent.select('table.Portal_Group_Table')[0]
            meetingElems = meetingsTable.contents
        except IndexError:
            # print('b:\nFailed at ' + str(classes) + ', ' + section + number)
            continue # no meetings (e.g. Internship)
        meetings = []
        for i in range(2, len(meetingElems) - 1):
            meeting = meetingElems[i]

            try:
                tds = meeting.find_all('td')
            except AttributeError:
                continue # porbably just a blank space

            # professor
            try:
                professor = tds[1].text.strip()
            except:
                professor = ''
            # building
            try:
                building = tds[2].text.split('-')[0].strip()
            except:
                building = ''
            # room
            try:
                room = tds[2].text.split('-')[1].strip()
            except:
                room = ''
            # days
            try:
                days = tds[3].text.strip()
            except:
                days = ''
            # weekly 4
            # start time
            try:
                start = tds[5].text.strip()
            except:
                start = '12:01:00 AM'
            # end time
            try:
                end = tds[6].text.strip()
            except:
                end = '11:59:00 PM'
            # total seats
            try:
                seatsMax = int(tds[7].text.strip())
            except:
                seatsMax = 0
            # seats that are taken
            try:
                seatsTaken = int(tds[8].text.strip())
            except:
                seatsTaken = 0

            timeObj = {
                'start': timeObjFromStr(start),
                'end': timeObjFromStr(end)
            }

            meetingObj = {
                'professor': professor,
                'campus': '',
                'building': building,
                'room': room,
                'days': days,
                'time': timeObj
            }
            # print(to2Str(timeObj.start.h) + to2Str(timeObj.start.m) + '-' + to2Str(timeObj.end.h) + to2Str(timeObj.end.m))
            meetings.append(meetingObj)

        # add this class' data to the list of class datas
        # print(number + section)
        classData = {
            'section': section,
            'meetings': meetings,
            'seatsMax': seatsMax,
            'seatsLeft': seatsMax - seatsTaken
            }
        try:
            classDataList[number].append(classData)
        except KeyError:
            classDataList[number] = [classData]

browser = mechanicalsoup.Browser()

# request cams login page. the resultis a reguests.Response object http://docs...
login_page = getPage(browser, 'login.asp')


# login_page.soup is a BeautifulSoup object http://...
# we grab the login form
login_form = login_page.soup.select('#frmLogin')[0]

# specify username, password, and semester
f = open('config.txt', 'r')
text = f.read()
username = text.split(': ')[1].split('\n')[0]
password = text.split(': ')[2].split('\n')[0]
semester = text.split(': ')[3].split('\n')[0]
toValue = login_form.select('#idterm')[0](text=semester)[0].parent['value']

# submit form
params = {  u'txtUsername': username,
            u'txtPassword': password,
            u'term': toValue,
            u'accessKey': '',
            u'op': 'login' }
page2 = postPage(browser, 'ceProcess.asp', params)

# verify we are now logged in
status = page2.soup.text.index('\'loginStatus\':\'true\'')
assert(status > 0)

print('Successfully signed in...')

# verify we remain logged in (thanks to cookies) as we browse the rest of the site
page3 = postPage(browser, 'cePortalOffering.asp', { u'page': u'1' })
assert(page3.soup('a', { 'class': 'button'}, text='Logout'))

# find out how many pages there are
a = page3.soup.select('.Portal_Grid_Pager')[0] # Portal_Grid_Pager
b = a.contents # children of Portal_Grid_Pager
c = b[len(b) - 1] # last child or Portal_Grid_Pager
d = c.split('Total Pages: ')[1].split(')')[0] # str(number of pages)
try:
    e = int(d) # integer number of pages
except ValueError:
    e = 0
assert(e > 0)

numPages = e

print('Page 1...')
getClassesFromPage(page3)

for i in range(2, numPages + 1):
    uPage = str(i)
    print('Page ' + uPage + '...')
    page = postPage(browser, 'cePortalOffering.asp', { u'page': uPage })
    getClassesFromPage(page)

print("Success! Check out output.json")

# pprint.PrettyPrinter(indent=2).pprint(classDataList)
fileOut = open('output.json', 'w+')
jsonData = json.dumps(classDataList, indent=4)
fileOut.write(jsonData)
