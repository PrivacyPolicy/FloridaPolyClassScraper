"""Example app to login to GitHub"""
import argparse
import mechanicalsoup

parser = argparse.ArgumentParser(description='Login to GitHub.')
parser.add_argument('username')
parser.add_argument('password')
args = parser.parse_args()

browser = mechanicalsoup.Browser()

# request githublogin page. the resultis a reguests.Response object http://docs...
login_page = browser.get('https://github.com/login')

# login_page.soup is a BeautifulSoup object http://...
# we grab the login form
login_form = login_page.soup.select('#login')[0].select('form')[0]

# specify username and password
login_form.select('#login_field')[0]['value'] = args.username
login_form.select('#password')[0]['value'] = args.password

# (or alternatively)
# login_form.input({'login': args.username, 'password': args.password})

# submit form
page2 = browser.submit(login_form, login_page.url)

# verify we are now logged in

messages = page2.soup.find('div', class_='flash-messages')
if messages:
    print(messages.text)
assert page2.soup.select('.logout-form')

print(page2.soup.title.text)

# verify we remain logged in (thanks to cookies) as we browse the rest of the site
page3 = browser.get('https://github.com/hickford/MechanicalSoup')
assert page3.soup.select('.logout-form')
