import requests
import unittest
import time

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException


class Nitro(unittest.TestCase):
    def setUp(self):
        # link to NBA basketball events
        self.sport = "NBA Basketball"
        url = 'https://sports.betcoin.ag/#/sport/1172'

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

    def test_main(self):
        formatterOut = '%a, %b %d, %Y %I:%M %p'
        formatterIn = '%d %b %Y, %H:%M'

        driver = self.driver
        sport = "NBA"
        # wait up to 20 seconds events to appear
        sportPath = "//*[text() = '"+ sport +"']"
        WebDriverWait(driver, 20).until( lambda driver: driver.find_element_by_xpath(sportPath))
        # javascript still might be loading elements

        eventsPage = BeautifulSoup(driver.page_source, "html.parser")
        sportContent = eventsPage.find(string = sport).parent.parent.next_sibling.next_sibling
        events = sportContent.find_all(title = "Basketball / NBA / NBA")

        allEvents = []
        for event in events:
            href = event.get("href")
            time = event.b.string
            name = event.contents[2].strip().replace(" - ", " vs ")
            year = str(datetime.now().year)
            time = time.replace(",", " "+year+",")
            date = datetime.strptime(time, formatterIn)
            timeStr = date.strftime(formatterOut)

            print timeStr
            print name

            matchPath = "(//a[contains(@href, '"+href+"')])"
            matchElement = driver.find_element_by_xpath(matchPath)
            matchElement.click()

            # must wait until total points section appears
            sectionPath = "//*[text() = 'Total Points']"
            WebDriverWait(driver, 10).until( lambda driver: driver.find_element_by_xpath(sectionPath))
            optionsPage = BeautifulSoup(driver.page_source, "html.parser")

            sections = ["Match Winner", "Points Handicap", "Total Points"]
            eventOptions = []
            for section in sections:
                h4 = optionsPage.find(string = section)
                if (h4 == None):
                    continue

                # need to skip comments to get to content
                sectionContent = h4.parent.parent.next_sibling.next_sibling.next_sibling.next_sibling
                options = sectionContent.find_all("div", {"class":"odd_team1"})

                for option in options:
                    optionName = option.get("title") + " ML" if (section == "Match Winner") else option.get("title")
                    odds = option.find("span", {"class":"coefficient"}).get_text().strip()
                    sportsEventOption = {
                        "name": optionName,
                        "odds": float(odds)
                        }
                    # log extracted content
                    print sportsEventOption
                    eventOptions.append(sportsEventOption)

            sportsEvent = {
                "name": name,
                "time": timeStr,
                "options": eventOptions
            }
            allEvents.append(sportsEvent)

            driver.back()
            WebDriverWait(driver, 20).until( lambda driver: driver.find_element_by_xpath(sportPath))

        blob = {
           "bookname": "Betcoin",
           "sport": self.sport,
           "events": allEvents
        }

        response = requests.post('http://localhost:9000/events', json=blob)
        print response.content

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
