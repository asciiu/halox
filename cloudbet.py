import requests
import re
import mechanize
from selenium import webdriver
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# link to NFL football events
url = 'https://www.cloudbet.com/en/sports/competition/208'
# link to NBA basketball events
url = 'https://www.cloudbet.com/en/sports/competition/143'

browser = mechanize.Browser()
browser.set_handle_equiv(True)
browser.set_handle_redirect(True)
browser.set_handle_referer(True)
browser.set_handle_robots(False)
browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
response = browser.open(url)

soup = BeautifulSoup(response.read(), "html.parser")

table = soup.find("table", { "class" : "sports-line" })
dates = []
for thead in table.findAll("thead"):
    header = thead.find('th')
    date = header.find('div', {'class':'sports-line-title'})
    dates.append(date.span.string)

#print dates

formatter = '%a, %b %d, %Y %I:%M %p'
date = ""
for row in table.findAll("tr"):
    # if row is header row
    thead = row.find_parent("thead")
    if (thead != None):
        div = row.find('div', {'class':'sports-line-title'})
        date = div.span.string
        continue

    time = row.find("div", {"class":"time"}).span.string
    fullDate = date + " " + time

    datetime = datetime.strptime(fullDate, formatter)
    # convert to mountain time
    datetime = datetime - timedelta(hours=7)

    description = row.find("td", {"class":"col2"})
    teamNames = row.findAll("div", {"class":"team-name-item"})

    # extract date from thead
    names = map(lambda x: x.string, teamNames)
    #date = datetime.strftime(formatter)
    #print date
    print names

    # follow event link
    response = browser.follow_link(url = description.a.get('href'))
    details = BeautifulSoup(response, "html.parser")
    spreads = details.find(string = "Points Spreads").find_parent("div").find_parent("div")
    btn = spreads.find("i")
    btn['class'] = 'icon-angle-up up'
    options = spreads

    print options

    browser.back()
    #print response

    #cells = row.findAll("td")
    #print cells

#for link in browser.links():
#    print link.text, link.url
