from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
#from TorCtl import TorCtl

import requests
import unittest


class Scrapper(unittest.TestCase):

    def renew_connection(self):
        conn = TorCtl.connect(controlAddr="127.0.0.1", controlPort=9051, passphrase="HackersAndSmakersComingToT0wn!")
        conn.send_signal("NEWNYM")
        conn.close()


    def snap_shot(self):
        self.driver.get_screenshot_as_file('/Users/bishop/Workspace/Python/halox/screenshots/test.png')


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


    def setUp(self):
        self.renew_connection()
        service_args = [
            '--proxy=127.0.0.1:8118',
            '--proxy-type=http',
        ]
        self.driver = webdriver.PhantomJS(service_args = service_args)
        self.driver.implicitly_wait(10)
        self.driver.set_window_size(1120, 550)


    def post_data(self, book, sport, events):
        blob = {
          "bookname": book,
          "sport": sport,
          "events": events
        }
        response = requests.post('http://localhost:9000/events', json=blob)
        print response.content


    #def test_login(self):
    #    driver = self.driver
    #    self.driver.get("http://icanhazip.com/")
    #    self.snap_shot()
    #    print "snap"


    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
