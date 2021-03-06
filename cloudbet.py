import requests
import unittest
import json
import time

from base import Scrapper
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException


class Cloudbet(Scrapper):
    def setUp(self):
        # link to NFL football events
        #url = 'https://www.cloudbet.com/en/sports/competition/208'
        # link to NBA basketball events
        self.sport = "NBA Basketball"
        url = 'https://www.cloudbet.com/en/sports/competition/143'
        #self.sport = "NCAA Basketball"
        #url = 'https://www.cloudbet.com/en/sports/competition/148'

        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1120, 550)
        self.driver.get(url)
        self.driver.implicitly_wait(10)


    def test_main(self):
        driver = self.driver
        self.bookname = "Cloudbet"

        WebDriverWait(driver, 20).until( lambda driver: driver.find_element_by_class_name("sports-line"))
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # table with class sports-line
        table = soup.find("table", { "class" : "sports-line" })
        # skip the live events table
        if "sports-line_live" in table["class"]:
            table = table.next_sibling

        formatter = '%a, %b %d, %Y %I:%M %p'
        date = ""
        allEvents = []
        for row in table.findAll("tr"):
            # if row is header row
            # get the date string
            thead = row.find_parent("thead")
            if (thead != None):
                div = row.find('div', {'class':'sports-line-title'})
                date = div.span.string
                continue

            # find the div with class time
            timeDiv = row.find("div", {"class":"time"})
            t = timeDiv.span.string
            # construct date plus time
            fullDate = date + " " + t

            t = datetime.strptime(fullDate, formatter)
            # convert to mountain time?
            #time = time - timedelta(hours=7)
            timeStr = t.strftime(formatter)

            # extract the team names
            description = row.find("td", {"class":"col2"})
            teamNames = row.findAll("div", {"class":"team-name-item"})
            names = map(lambda x: x.string, teamNames)
            # log the date and names
            print timeStr
            print names

            # execute a click to view the event details
            href = description.a.get("href")
            gamePath = "(//a[contains(@href, '"+href+"')])"
            gameElement = driver.find_element_by_xpath(gamePath)
            gameElement.click()

            # must wait until moneyline section appears
            sectionPath1 = "//*[text() = 'US Total']"
            sectionPath2 = "//*[text() = 'Moneyline']"
            try:
                WebDriverWait(driver, 20).until( lambda driver: driver.find_element_by_xpath(sectionPath1 or sectionPath2))
            except TimeoutException:
                self.snap_shot

            spreadsPage = BeautifulSoup(driver.page_source, "html.parser")

            sectionDivs = spreadsPage.find_all("div", {"class":"market-list__item__title"})
            sectionTitles = map(lambda div: div.get_text(), sectionDivs)
            sectionTitles

            # these are the sections we extract odds from
            sections = ["Moneyline", "Points Spreads", "Total Spreads"]
            eventOptions = []
            for section in sections:
                # skip sections not present
                if (section not in sectionTitles):
                    print section + " not found"
                    continue

                # skip locked sections
                sectionDiv = spreadsPage.find(string = section).parent.parent
                if ("locked" in sectionDiv.get("class")):
                    continue

                # find the section of interest and expand the options
                linePath = "//*[text() = '"+section+"']"
                spreads = driver.find_element_by_xpath(linePath)
                spreads.click()

                page2 = BeautifulSoup(driver.page_source, "html.parser")
                pointSpreads = page2.find(string = section).parent.parent
                options = pointSpreads.find_all("div", {"class":"name"})

                for option in options:
                    optionName = option.string
                    if (optionName == None):
                      optionName = option.contents[1].string + " " + option.contents[6].string

                    if (section == "Moneyline"):
                      optionName = optionName + " ML"

                    odds = option.next_sibling.get_text()
                    sportsEventOption = {
                        "name": optionName,
                        "odds": float(odds)
                        }
                    # log extracted content
                    print sportsEventOption
                    eventOptions.append(sportsEventOption)

            sportsEvent = {
                "name": names[0] + " vs " + names[1],
                "time": timeStr,
                "options": eventOptions
            }
            if eventOptions:
                self.post_data(self.bookname, self.sport, [sportsEvent])

            # previous page
            driver.back()
            WebDriverWait(driver, 20).until( lambda driver: driver.find_element_by_class_name("sports-line-title"))


    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
