import requests
import re
import mechanize
import unittest

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

class Cloudbet(unittest.TestCase):
    def setUp(self):
        # link to NFL football events
        url = 'https://www.cloudbet.com/en/sports/competition/208'
        # link to NBA basketball events
        url = 'https://www.cloudbet.com/en/sports/competition/143'

        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1120, 550)
        self.driver.get(url)

    def test_main(self):
        driver = self.driver
        soup = BeautifulSoup(driver.page_source, "html.parser")

        table = soup.find("table", { "class" : "sports-line" })
        if "sports-line_live" in table["class"]:
            table = table.next_sibling

        formatter = '%a, %b %d, %Y %I:%M %p'
        date = ""
        for row in table.findAll("tr"):
            # if row is header row
            thead = row.find_parent("thead")
            if (thead != None):
                div = row.find('div', {'class':'sports-line-title'})
                date = div.span.string
                continue

            timeDiv = row.find("div", {"class":"time"})
            time = timeDiv.span.string
            fullDate = date + " " + time

            time = datetime.strptime(fullDate, formatter)
            # convert to mountain time?
            #time = time - timedelta(hours=7)
            timeStr = time.strftime(formatter)

            # extract the team names
            description = row.find("td", {"class":"col2"})
            teamNames = row.findAll("div", {"class":"team-name-item"})
            names = map(lambda x: x.string, teamNames)
            #date = datetime.strftime(formatter)
            #print date
            print timeStr
            print names

            href = description.a.get("href")
            gamePath = "(//a[contains(@href, '"+href+"')])"
            gameElement = driver.find_element_by_xpath(gamePath)
            gameElement.click()

            linePath = "//*[text() = 'Points Spreads']"
            spreads = WebDriverWait(driver, 10).until( lambda driver: driver.find_element_by_xpath(linePath))

            spreads.click()
            page2 = BeautifulSoup(driver.page_source, "html.parser")
            pointSpreads = page2.find(string = "Points Spreads").parent.parent
            options = pointSpreads.find_all("div", {"class":"name"})
            for option in options:
                optionName = option.string
                odds = option.next_sibling.get_text()
                print optionName + " " + odds

            driver.back()
            WebDriverWait(driver, 10).until( lambda driver: driver.find_element_by_xpath(gamePath))
            # follow event link

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
