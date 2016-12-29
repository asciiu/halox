import requests
import unittest
import time

from base import Scrapper
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException


class Nitro(Scrapper):
    def setUp(self):
        # link to NBA basketball events
        self.sport = "NBA Basketball"
        url = 'https://nitrogensports.eu/sport/football/nfl'
        url = 'https://nitrogensports.eu/sport/basketball/nba'

        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(2560, 1600)
        self.driver.implicitly_wait(10)
        self.driver.get(url)

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
        driver = self.driver

        # wait up to 10 seconds for signin btn to appear
        signInBtn = WebDriverWait(driver, 20).until( lambda driver: driver.find_element_by_id("modal-welcome-new-button"))
        # dead wait for modal to slide into view
        time.sleep(2)
        # create anonymous new account
        signInBtn.click()

        # wait until event search shows up
        WebDriverWait(driver, 10).until( lambda driver: driver.find_element_by_class_name("events-result-set"))
        time.sleep(2)

        page = BeautifulSoup(driver.page_source, "html.parser")
        resultSet = page.find("div", {"class":"events-result-set"})
        events = resultSet.find_all("div", {"class":"event"})

        # loop through the events
        for event in events:
            contents = event.find("div", {"class":"event-participants"}).contents
            name = contents[1] + contents[3]
            date = event.find("span", {"class":"event-time-text"}).string
            timeStr = self.format_date(date)

            print timeStr
            print name

            # loop through the option rows
            rows = event.find_all("div", {"class":"event-row"})
            eventOptions = []
            for row in rows:
                # this is the participant's name or option name in the first cell
                part = row.find("div", {"class":"event-participant"}).contents[0]
                # all odds for this selection
                allOptions = row.find("div", {"class":"event-odds"}).find_all("a", {"class":"selectboxit-option-anchor"})

                for option in allOptions:
                    contents = option.contents
                    oddsText = contents[1].split(" ")
                    odds = float(oddsText[1])
                    sportsEventOption = {
                        "name": part + " " + oddsText[0],
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

            if eventOptions:
                self.post_data("Nitrogen Sports", self.sport, [sportsEvent])


if __name__ == "__main__":
    unittest.main()
