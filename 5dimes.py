import requests
import unittest
import time
import json

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException


class FiveDimes(unittest.TestCase):
    def setUp(self):
        self.sport = "NBA Basketball"
        url = 'http://www.5dimes.eu/default.asp'

        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(2560, 1600)
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


    def snap_shot(self):
        self.driver.get_screenshot_as_file('/Users/bishop/Workspace/Python/scrapers/screenshots/test.png')


    def format_date(self, txt):
        timeText = txt.strip()
        # convert full day to abrev
        day = timeText.split(",")[0];
        timeText = timeText.replace(day, day[:3])
        # convert month to 3 letter formatted
        month = timeText.split(" ")[1];
        timeText = timeText.replace(month, month[:3])
        timeText = timeText.replace("pm", " PM")
        timeText = timeText.replace("am", " AM")
        return timeText


    def login(self):
        driver = self.driver
        userPath = "//input[@name='customerID']"
        username = driver.find_element_by_xpath(userPath)
        passPath = "//input[@name='password']"
        password = driver.find_element_by_xpath(passPath)

        username.send_keys("5D2336024")
        password.send_keys("MeKernel78")

        loginPath = "//input[@name='submit1']"
        loginBtn = driver.find_element_by_xpath(loginPath)
        loginBtn.click()

    def sports_event_option(self, name, odds):
        return {
            "name": name,
            "odds": float(odds)
        }

    def post_data(self, events):
        blob = {
          "bookname": "5Dimes",
          "sport": self.sport,
          "events": events
        }
        response = requests.post('http://localhost:9000/events', json=blob)
        print response.content


    def extract_row_info(self, row):
        # time
        firstElement = row.contents[0].string.replace("PM", " PM").replace("AM", " AM").strip()
        # option name
        optionName = row.contents[2].string
        optionName = optionName.split(u'\xa0')[1]
        # spread option
        spreadOption = row.contents[3].string
        spreadOption = spreadOption.replace(u"\xbd", '.5').replace(u"\xa0", "").strip().split(" ")
        # total option
        totalOption = row.contents[5].string
        totalOption = totalOption.replace(u"\xbd", '.5').replace(u"\xa0", "").replace('o', "Over ").replace('u', "Under ")

        groups = totalOption.split(' ')
        totalOption = ' '.join(groups[:2]), ' '.join(groups[2:])

        option1 = self.sports_event_option(optionName + " " + spreadOption[0], spreadOption[1])
        option2 = self.sports_event_option(totalOption[0], totalOption[1])

        return (firstElement, [option1, option2])


    def test_main(self):
        formatterOut = '%a, %b %d, %Y %I:%M %p'
        formatterIn = '%a %m/%d %Y %I:%M %p'

        driver = self.driver
        sport = "Basketball_NBA"

        self.login()

        # wait for sport to appear
        checkbox = WebDriverWait(driver, 10).until( lambda driver: driver.find_element_by_id(sport))
        checkbox.click()

        continuePath = "//input[@value='Continue']"
        continueBtn = driver.find_element_by_xpath(continuePath)
        continueBtn.click()

        eventsPage = BeautifulSoup(driver.page_source, "html.parser")
        contents = eventsPage.find("div", {"id":"contentContainer"})

        # first lines container
        firstLineContainer = contents.find("div", {"class":"linesContainer"})

        headers = firstLineContainer.find_all("tr", {"class":"linesSubHeader"})

        for header in headers:
            eventName = header.get_text().strip()

            linesRow = header.next_sibling
            row1Data = self.extract_row_info(linesRow)

            linesBotRow = linesRow.next_sibling
            row2Data = self.extract_row_info(linesBotRow)

            year = str(datetime.now().year)
            date = row1Data[0] + " " + year + " " + row2Data[0]
            date = datetime.strptime(date, formatterIn)

            name = eventName.replace(" at ", " vs ")
            date = date.strftime(formatterOut)

            print date
            print name
            print row1Data[1]
            print row2Data[1]

            sportsEvent = {
                "name": eventName.replace(" at ", " vs "),
                "time": date,
                "options": row1Data[1] + row2Data[1]
            }
            self.post_data([sportsEvent])

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
