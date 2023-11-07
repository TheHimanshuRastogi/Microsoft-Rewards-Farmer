"""
This is a module docstring
"""

from src.logger import logger
from src.browser import Browser
from .activities import Activities


class MorePromotions:
    def __init__(self, browser: Browser):
        self.browser = browser
        self.activities = Activities(browser)

    def completeMorePromotions(self):
        logger.info("[MORE PROMO] " + "Trying to complete More Promotions...")
        morePromotions = self.browser.utils.getDashboardData()["morePromotions"]
        i = 0
        for promotion in morePromotions:
            try:
                i += 1
                if (
                    promotion["complete"] is False
                    and promotion["pointProgressMax"] != 0
                ):
                    self.activities.openMorePromotionsActivity(i)
                    if promotion["promotionType"] == "urlreward":
                        self.activities.completeSearch()
                    elif (
                        promotion["promotionType"] == "quiz"
                        and promotion["pointProgress"] == 0
                    ):
                        if promotion["pointProgressMax"] == 10:
                            self.activities.completeABC()
                        elif promotion["pointProgressMax"] in [30, 40]:
                            self.activities.completeQuiz()
                        elif promotion["pointProgressMax"] == 50:
                            self.activities.completeThisOrThat()
                    else:
                        self.activities.completeSearch()
            except Exception:  # pylint: disable=broad-except
                self.browser.utils.resetTabs()
        logger.info("[MORE PROMO] Completed More Promotions successfully!")
