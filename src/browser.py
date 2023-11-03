"""
This is a module docstring
"""

import os
import logging
import contextlib
from typing import Any

import ipapi
from selenium import webdriver
try:
    import seleniumwire.undetected_chromedriver as uc
except ImportError:
    pass

from src.os import OS
from src.utils import Utils
from src.userAgentGenerator import GenerateUserAgent


class Browser:
    """WebDriver wrapper class."""

    def __init__(self, mobile: bool, account, args: Any) -> None:
        
        self.os = OS()
        self.mobile = mobile
        self.browserType = "mobile" if mobile else "desktop"
        self.headless = False or args.visible
        self.email = account["email"]
        self.password = account["password"]
        self.localeLang, self.localeGeo = self.getGeoLand(args.lang, args.geo)
        self.proxy = None

        if args.proxy:
            self.proxy = args.proxy
        elif account.get("proxy"):
            self.proxy = account["proxy"]

        self.userAgent, self.userAgentMetadata = GenerateUserAgent().userAgent(self.mobile)

        self.webdriver = self.browserSetup()
        self.utils = Utils(self.webdriver)

    def browserSetup(self):
        """Setup browser and return webdriver.Chrome (controllable browser)"""

        #-------------------Chrome-Options------------------# 

        options = webdriver.ChromeOptions()
        options.add_argument(f"--lang={self.localeLang}")
        options.add_argument("--log-level=3")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-certificate-errors-spki-list")
        options.add_argument("--ignore-ssl-errors")
        if not self.headless:
            options.add_argument("--headless")
        if self.os.windows:
            options.add_argument(f"--user-data-dir={os.getcwd()}/ChromeData")
            options.add_argument(f"--profile-directory={self.email}")


        #-----------------------Proxies---------------------# 

        seleniumwireOptions: dict[str, Any] = {"verify_ssl": False}

        if self.proxy:
            seleniumwireOptions["proxy"] = {
                "http": self.proxy,
                "https": self.proxy,
                "no_proxy": "localhost,127.0.0.1",
            }

        #-----------------------WebDriver---------------------# 

        if self.os.linux:
            driver = uc.Chrome(
                options=options,
                seleniumwire_options=seleniumwireOptions
            )
            
        elif self.os.windows:
            driver = webdriver.Chrome(options)

        #------------------Browser-Configration----------------# 

        if self.mobile:
            deviceHeight = 800
            deviceWidth = 400
            screenHeight = deviceHeight + 146
            screenWidth = deviceWidth
            
        else:
            deviceWidth = 1800
            deviceHeight = 900
            screenWidth = deviceWidth + 55
            screenHeight = deviceHeight + 151        

        if self.mobile:
            driver.execute_cdp_cmd(
                "Emulation.setTouchEmulationEnabled",
                {
                    "enabled": True,
                },
            )

        driver.execute_cdp_cmd(
            "Emulation.setDeviceMetricsOverride",
            {
                "width": deviceWidth,
                "height": deviceHeight,
                "deviceScaleFactor": 0,
                "mobile": self.mobile,
                "screenWidth": screenWidth,
                "screenHeight": screenHeight,
                "positionX": 0,
                "positionY": 0,
                 "viewport": {
                    "x": 0,
                    "y": 0,
                    "width": deviceWidth,
                    "height": deviceHeight,
                    "scale": 1,
                },
            },
        )

        driver.execute_cdp_cmd(
            "Emulation.setUserAgentOverride",
            {
                "userAgent": self.userAgent,
                "platform": self.userAgentMetadata["platform"],
                "userAgentMetadata": self.userAgentMetadata,
            },
        )

        #------------------------Others----------------------# 

        seleniumLogger = logging.getLogger("seleniumwire")
        seleniumLogger.setLevel(logging.ERROR)

        logging.info(
            f"[BROWSER] Working with {self.browserType.capitalize()} browser..."
        )

        return driver 

    def getGeoLand(self, lang: str, geo: str) -> tuple:
        if lang is None or geo is None:
            try:
                nfo = ipapi.location()
                if isinstance(nfo, dict):
                    if lang is None:
                        lang = nfo["languages"].split(",")[0].split("-")[0]
                    if geo is None:
                        geo = nfo["country"]
            except Exception:  # pylint: disable=broad-except
                return ("en", "US")
        return (lang, geo)
    
    def closeBrowser(self) -> None:
        """Perform actions to close the browser cleanly."""
        logging.info(
            f"[BROWSER] Closing {self.browserType.capitalize()} browser!"
        )

        with contextlib.suppress(Exception):
            self.webdriver.quit()

    def __enter__(self) -> "Browser":
        """Enter context manager"""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context manager"""
        self.closeBrowser()
