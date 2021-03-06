#Copyright 2007-2009 WebDriver committers
#Copyright 2007-2009 Google Inc.
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import InvalidElementStateException
from selenium.common.exceptions import NoAlertPresentException

import unittest

@pytest.mark.ignore_opera
class AlertsTest(unittest.TestCase):

    def testShouldBeAbleToOverrideTheWindowAlertMethod(self):
        self._loadPage("alerts")
        self.driver.execute_script(
            "window.alert = function(msg) { document.getElementById('text').innerHTML = msg; }")
        self.driver.find_element(by=By.ID, value="alert").click()
        try:
            self.assertEqual(self.driver.find_element_by_id('text').text, "cheese")
        except Exception, e:
            # if we're here, likely the alert is displayed
            # not dismissing it will affect other tests
            try:
                self._waitForAlert().dismiss()
            except Exception:
                pass
            raise e

    def testShouldAllowUsersToAcceptAnAlertManually(self):
        self._loadPage("alerts")
        self.driver.find_element(by=By.ID, value="alert").click()
        alert = self._waitForAlert()
        alert.accept()
        #  If we can perform any action, we're good to go
        self.assertEqual("Testing Alerts", self.driver.title)

    def testShouldAllowUsersToAcceptAnAlertWithNoTextManually(self):
        self._loadPage("alerts")
        self.driver.find_element(By.ID,"empty-alert").click();
        alert = self._waitForAlert()
        alert.accept()

        #  If we can perform any action, we're good to go
        self.assertEqual("Testing Alerts", self.driver.title)

    def testShouldGetTextOfAlertOpenedInSetTimeout(self):
        self._loadPage("alerts")
        self.driver.find_element_by_id("slow-alert").click()

        # DO NOT WAIT OR SLEEP HERE
        # This is a regression test for a bug where only the first switchTo call would throw,
        # and only if it happens before the alert actually loads.

        alert = self._waitForAlert()
        try:
            self.assertEqual("Slow", alert.text)
        finally:
            alert.accept()

    @pytest.mark.ignore_chrome
    def testShouldAllowUsersToDismissAnAlertManually(self):
        self._loadPage("alerts")
        self.driver.find_element(by=By.ID, value="alert").click()
        alert = self._waitForAlert()
        alert.dismiss()
        #  If we can perform any action, we're good to go
        self.assertEqual("Testing Alerts", self.driver.title)

    def testShouldAllowAUserToAcceptAPrompt(self):
        self._loadPage("alerts")
        self.driver.find_element(by=By.ID, value="prompt").click()
        alert = self._waitForAlert()
        alert.accept()

        #  If we can perform any action, we're good to go
        self.assertEqual("Testing Alerts", self.driver.title)

    def testShouldAllowAUserToDismissAPrompt(self):
        self._loadPage("alerts")
        self.driver.find_element(by=By.ID, value="prompt").click()
        alert = self._waitForAlert()
        alert.dismiss()

        #  If we can perform any action, we're good to go
        self.assertEqual("Testing Alerts", self.driver.title)

    def testShouldAllowAUserToSetTheValueOfAPrompt(self):
        self._loadPage("alerts")
        self.driver.find_element(by=By.ID, value="prompt").click()
        alert = self._waitForAlert()
        alert.send_keys("cheese")
        alert.accept()

        result = self.driver.find_element(by=By.ID, value="text").text
        self.assertEqual("cheese", result)

    def testSettingTheValueOfAnAlertThrows(self):
        self._loadPage("alerts")
        self.driver.find_element(By.ID,"alert").click();

        alert = self._waitForAlert()
        try:
            alert.send_keys("cheese");
            self.fail("Expected exception");
        except ElementNotVisibleException:
            pass
        except InvalidElementStateException:
            pass
        finally:
            alert.accept()

    def testAlertShouldNotAllowAdditionalCommandsIfDimissed(self):
        self._loadPage("alerts");
        self.driver.find_element(By.ID, "alert").click()

        alert = self._waitForAlert()
        alert.dismiss()

        try:
            alert.text
            self.fail("Expected NoAlertPresentException")
        except NoAlertPresentException:
            pass

    def testShouldAllowUsersToAcceptAnAlertInAFrame(self):
        self._loadPage("alerts")
        self.driver.switch_to_frame("iframeWithAlert")
        self.driver.find_element_by_id("alertInFrame").click()

        alert = self._waitForAlert()
        alert.accept()

        self.assertEqual("Testing Alerts", self.driver.title)

    def testShouldAllowUsersToAcceptAnAlertInANestedFrame(self):
        self._loadPage("alerts")
        self.driver.switch_to_frame("iframeWithIframe")
        self.driver.switch_to_frame("iframeWithAlert")

        self.driver.find_element_by_id("alertInFrame").click()

        alert = self._waitForAlert()
        alert.accept()

        self.assertEqual("Testing Alerts", self.driver.title)

    def testShouldThrowAnExceptionIfAnAlertHasNotBeenDealtWithAndDismissTheAlert(self):
        pass
        # //TODO(David) Complete this test

    def testPromptShouldUseDefaultValueIfNoKeysSent(self):
        self._loadPage("alerts")
        self.driver.find_element(By.ID, "prompt-with-default").click()

        alert = self._waitForAlert()
        alert.accept()

        txt = self.driver.find_element(By.ID, "text").text
        self.assertEqual("This is a default value", txt)

    def testPromptShouldHaveNullValueIfDismissed(self):
        self._loadPage("alerts")
        self.driver.find_element(By.ID, "prompt-with-default").click()
        alert = self._waitForAlert()
        alert.dismiss()

        self.assertEqual("null", self.driver.find_element(By.ID, "text").text)

    def testHandlesTwoAlertsFromOneInteraction(self):
        self._loadPage("alerts")

        self.driver.find_element(By.ID, "double-prompt").click()

        alert1 = self._waitForAlert()
        alert1.send_keys("brie")
        alert1.accept()

        alert2 = self._waitForAlert()
        alert2.send_keys("cheddar")
        alert2.accept();

        self.assertEqual(self.driver.find_element(By.ID, "text1").text, "brie")
        self.assertEqual(self.driver.find_element(By.ID, "text2").text, "cheddar")
    def testShouldHandleAlertOnPageLoad(self):
        self._loadPage("alerts")
        self.driver.find_element(By.ID, "open-page-with-onload-alert").click()
        alert = self._waitForAlert()
        value = alert.text
        alert.accept()

        self.assertEquals("onload", value)

    def testShouldAllowTheUserToGetTheTextOfAnAlert(self):
        self._loadPage("alerts")
        self.driver.find_element(by=By.ID, value="alert").click()
        alert = self._waitForAlert()
        value = alert.text
        alert.accept()
        self.assertEqual("cheese", value)
    
    def _waitForAlert(self):
        return WebDriverWait(self.driver, 3).until(EC.alert_is_present())

    def _pageURL(self, name):
        return "http://localhost:%d/%s.html" % (self.webserver.port, name)

    def _loadSimplePage(self):
        self._loadPage("simpleTest")

    def _loadPage(self, name):
        try:
            # just in case a previous test left open an alert
            self.driver.switch_to_alert().dismiss()
        except:
            pass
        self.driver.get(self._pageURL(name))
