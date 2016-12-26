from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

import unittest

class LoginTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.PhantomJS()
        self.driver.get("https://www.facebook.com")

    def test_login(self):
        driver = self.driver
        facebookusername = "Luke"
        password = "123456"
        emailFieldId = "email"
        passFieldId = "pass"
        loginBtnXPath = "//input[@value='Log In']"
        signupXPath = "(//a[contains(@href, '/r.php?locale=en_SP')])"

        emailFieldElement = WebDriverWait(driver, 10).until( lambda driver: driver.find_element_by_id(emailFieldId))
        passFieldElement = WebDriverWait(driver, 10).until( lambda driver: driver.find_element_by_id(passFieldId))
        loginFieldElement = WebDriverWait(driver, 10).until( lambda driver: driver.find_element_by_xpath(loginBtnXPath))

        emailFieldElement.clear()
        emailFieldElement.send_keys(facebookusername)
        passFieldElement.clear()
        passFieldElement.send_keys(password)
        loginFieldElement.click()

        signUpFieldElement = WebDriverWait(driver, 10).until( lambda driver: driver.find_element_by_xpath(signupXPath))

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
