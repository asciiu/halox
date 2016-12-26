import requests
import re
import mechanize
import unittest
import json
import urllib2
import time

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException


class SportsBet(unittest.TestCase):
    def setUp(self):
        # link to NBA basketball events
        self.sport = "NBA Basketball"
        self.sport = "Basketball NBA"
        url = 'https://sportsbet.io/sports'

        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1120, 550)
        self.driver.implicitly_wait(10)
        self.driver.get(url)

    def check_exists_by_class(self, classname):
        try:
            self.driver.find_element_by_class_name(classname)
        except NoSuchElementException:
            return False
        return True

    def check_exists_by_xpath(self, path):
        try:
            self.driver.find_element_by_xpath(path)
        except NoSuchElementException:
            return False
        return True

    def test_main(self):
        driver = self.driver
        formatter1 = '%d %b %y'
        formatter2 = '%d.%m.%Y'
        formatter3 = '%d.%m.%Y %H:%M'
        formatter4 = '%a, %b %d, %Y %I:%M %p'

        sportPath = "//*[text() = '"+self.sport+"']"
        sportElement = driver.find_element_by_xpath(sportPath)
        sportElement.click()

        dates = driver.find_element_by_class_name("date-badges-container")
        page = BeautifulSoup(driver.page_source, "html.parser")

        allEvents = []
        dateElements = page.find_all("div", {"class": "date-badge"})
        for element in dateElements:
            date = element.get_text().split(" ", 1)[1]

            if (date == "Matches"):
                continue

            datePath = "//*[text() = '"+date+"']"
            dateObj = driver.find_element_by_xpath(datePath)
            dateObj.click()

            formattedTime1 = datetime.strptime(date, formatter1)
            date = formattedTime1.strftime(formatter2)
            datePath2 = "//*[text() = '"+date+" ']"

            if self.check_exists_by_xpath(datePath2) is not True:
                continue
            else:
                page2 = BeautifulSoup(driver.page_source, "html.parser")
                events = page2.find_all("div", {"class":"event"})
                for evt in events:
                    content = evt.getText()
                    if "Markets will be available soon" in content:
                        continue

                    t = evt.find("div", {"class":"start"})
                    description = evt.find("div", {"class":"description"})
                    if (description == None):
                        continue

                    t = t.getText().split("Starts")[0]
                    t = ' '.join(t.split())
                    t = datetime.strptime(t, formatter3)
                    name = description.find("b").string

                    detailPath = "//*[text() = '"+name+"']"
                    detailElement = driver.find_element_by_xpath(detailPath)
                    detailElement.click()

                    linePath = "//*[text() = 'Points Spreads']"
                    spreads = WebDriverWait(driver, 10).until( lambda driver: driver.find_element_by_xpath(linePath))
                    time.sleep(2)

                    # extract spreads here
                    page3 = BeautifulSoup(driver.page_source, "html.parser")

                    sections = ["Match Winner", "Total Spreads", "Points Spreads"]
                    eventOptions = []
                    for section in sections:

                        optionDiv = page3.find(string = section).parent.parent.parent
                        options = optionDiv.find_all("div", {"class":"cell"}) if (section != "Points Spreads") else optionDiv.find_all("a", {"class":"cell"})

                        for option in options:
                            optionName = option.find("span", {"class":"truncate"}).string
                            optionName = optionName.lower().title()
                            optionName = optionName + " ML" if (section == "Match Winner") else optionName
                            odds = option.find("div", {"class":"odds"})

                            sportsEventOption = {
                                "name": optionName,
                                "odds": float(odds.string)
                            }
                            eventOptions.append(sportsEventOption)

                    timeStr =  t.strftime(formatter4)
                    matchName = name.lower().title().replace(" V ", " vs ")
                    sportsEvent = {
                        "name": matchName,
                        "time": timeStr,
                        "options": eventOptions
                    }
                    allEvents.append(sportsEvent)

                    driver.back()
                    WebDriverWait(driver, 10).until( lambda driver: driver.find_element_by_xpath(datePath2))

        blob = {
          "bookname": "SportsBet",
          "sport": self.sport,
          "events": allEvents
        }

        response = requests.post('http://localhost:9000/events', json=blob)
        print response.content

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
