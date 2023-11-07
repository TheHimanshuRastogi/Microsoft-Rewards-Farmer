"""
This is a module docstring
"""


import time
import contextlib
import urllib.parse

from selenium.webdriver.common.by import By

from src.logger import logger
from src.browser import Browser


class Login:
    def __init__(self, browser: Browser):
        self.browser = browser
        self.webdriver = browser.webdriver
        self.utils = browser.utils

    def login(self):

        logger.info("[LOGIN] " + "Checking if already Logged-in...", tg=True)
        logged_in = self._checkBingLogin()
        if logged_in:
            logger.info("[LOGIN] " + "Already Logged-in!", tg=True)
            self.utils.goHome()
            return
        
        logger.info("[LOGIN] " + "Trying to login...")
        self.webdriver.get("https://login.live.com/")
        alreadyLoggedIn = False
        while True:
            try:
                self.utils.waitUntilVisible(
                    By.CSS_SELECTOR, 'html[data-role-name="MeePortal"]', 0.1
                )
                alreadyLoggedIn = True
                break
            except Exception:  # pylint: disable=broad-except
                try:
                    self.utils.waitUntilVisible(By.ID, "loginHeader", 0.1)
                    break
                except Exception:  # pylint: disable=broad-except
                    if self.utils.tryDismissAllMessages():
                        continue

        if not alreadyLoggedIn:
            self._executeLogin()
        self.utils.tryDismissCookieBanner()

        logger.info("[LOGIN] " + "Logged-in!")
        self.utils.goHome()
        return

    def _executeLogin(self):
        self.utils.waitUntilVisible(By.ID, "loginHeader", 10)
        logger.info("[LOGIN] " + "Writing email...")
        self.webdriver.find_element(By.NAME, "loginfmt").send_keys(
            self.browser.email
        )
        self.webdriver.find_element(By.ID, "idSIButton9").click()

        try:
            self._enterPassword(self.browser.password)
        except Exception:  # pylint: disable=broad-except
            logger.error("[LOGIN] " + "2FA required !", tg=True)
            with contextlib.suppress(Exception):
                code = self.webdriver.find_element(
                    By.ID, "idRemoteNGC_DisplaySign"
                ).get_attribute("innerHTML")
                logger.error("[LOGIN] " + f"2FA code: {code}")
            logger.info("[LOGIN] Press enter when confirmed...")
            input()

        while not (
            urllib.parse.urlparse(self.webdriver.current_url).path == "/"
            and urllib.parse.urlparse(self.webdriver.current_url).hostname
            == "account.microsoft.com"
        ):
            self.utils.tryDismissAllMessages()
            time.sleep(1)

        self.utils.waitUntilVisible(
            By.CSS_SELECTOR, 'html[data-role-name="MeePortal"]', 10
        )

    def _enterPassword(self, password):
        self.utils.waitUntilClickable(By.NAME, "passwd", 10)
        self.utils.waitUntilClickable(By.ID, "idSIButton9", 10)
        # browser.webdriver.find_element(By.NAME, "passwd").send_keys(password)
        # If password contains special characters like " ' or \, send_keys() will not work
        password = password.replace("\\", "\\\\").replace('"', '\\"')
        self.webdriver.execute_script(
            f'document.getElementsByName("passwd")[0].value = "{password}";'
        )
        logger.info("[LOGIN] " + "Writing password...")
        self.webdriver.find_element(By.ID, "idSIButton9").click()
        time.sleep(3)

    def _checkBingLogin(self):
        self.webdriver.get(
            "https://www.bing.com/fd/auth/signin?action=interactive&provider=windows_live_id&return_url=https://www.bing.com"
        )
        while True:
            currentUrl = urllib.parse.urlparse(self.webdriver.current_url)
            
            if currentUrl.hostname == "www.bing.com" and currentUrl.path == "/":
                time.sleep(3)
                self.utils.tryDismissBingCookieBanner()
                with contextlib.suppress(Exception):
                    if self.utils.checkBingLogin():
                        return True  # User is logged in, exit loop
            else: # If the user is not on the main Bing page, check for a redirect
                redirected = self._checkForRedirect()
                if redirected:
                    return True  # User is logged in, exit loop
                
            time.sleep(1)

    def _checkForRedirect(self):
        """This function checks for redirection after logging in"""
        for _ in range(10):
            currentUrl = urllib.parse.urlparse(self.webdriver.current_url)
            if currentUrl.hostname == "www.bing.com" and currentUrl.path == "/":
                return True  # User is logged in, exit loop
            time.sleep(2)  # Wait and check again
        return False  # If not logged in, exit the function with False