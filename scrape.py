import argparse
import mechanicalsoup
import pathlib
import html5lib
from bs4 import BeautifulSoup

baseURL = 'https://cams.floridapoly.org/Student/'

def getPage(browser, fileName):
    try:
        page = browser.get(baseURL + fileName)
    except:
        page = type('obj', (object,), {'content': '', 'soup': ''})
        page.content = open('_cache/' + fileName + '.html', 'r').read()
        page.soup = BeautifulSoup(page.content, 'html5lib')
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
        page.soup = BeautifulSoup(page.content, 'html5lib')
    return page

def getClassesFromPage(page):
    soup = page.soup
    classes = soup.select('tr.courseInfo')
    classDataList = {}
    for theClass in classes:
        tds = theClass.find_all('td')

        # course number; solely for identification purposes
        number = str(tds[0].contents[0]).strip()

        # get a list of meeting times
        print(theClass)
        print('\n\n\n --------------------- \n\n\n')
        print(theClass.parent.contents[4])
        print('\n\n\n --------------------- \n\n\n')
        print(theClass.next_element.next_elements)
        print('\n\n\n --------------------- \n\n\n')
        meetingsContainer = theClass.next_element.next_element
        meetingsElem = meetingsContainer.select('tr.headerRow')[0]
        meetings = []
        # print(meetingsContainer)
        # print(meetingsElem)
        # print(meetings)
        try:
            while True:
                meeting = meetingsElem.next_element
                meetings.append(meeting.find_all('td')[1].text)
        except AttributeError:
            pass # ran out of class meetings

        # add this class' data to the list of class datas
        classData = {
            'times': meetings}
        try:
            classDataList[number].append(classData)
        except KeyError:
            classDataList[number] = [classData]
    return classDataList

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

print('Successfully signed in')

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

classes = getClassesFromPage(page3)
print('1-----------------------------')
print(str(classes).replace('},', '},\n'))
print('-------------------------------\n')

# for i in range(2, numPages + 1):
if False:
    uPage = str(i)
    page = postPage(browser, 'cePortalOffering.asp', { u'page': uPage })
    classes = getClassesFromPage(page)
    print(uPage + '-----------------------------')
    print(str(classes).replace('},', '},\n'))
    print('-------------------------------\n')
