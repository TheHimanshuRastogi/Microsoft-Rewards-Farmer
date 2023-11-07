"""
This is a module docstring
"""


import json
import logging
import argparse
from pathlib import Path
from random import shuffle

from src.logger import logger
from src import Browser, Notifier, DailySet, Login, MorePromotions, PunchCards, Searches


def main():
    notifier = Notifier()
    args = argumentParser()
    loadedAccounts = setupAccounts()
    for currentAccount in loadedAccounts:
        try:
            executeBot(currentAccount, notifier, args)
        except Exception as e:
            logging.exception(f"{e.__class__.__name__}: {e}")


def argumentParser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Microsoft Rewards Farmer")
    parser.add_argument(
        "-v", "--visible", action="store_true", help="Optional: Visible browser"
    )
    parser.add_argument(
        "-l", "--lang", type=str, default=None, help="Optional: Language (ex: en)"
    )
    parser.add_argument(
        "-g", "--geo", type=str, default=None, help="Optional: Geolocation (ex: US)"
    )
    parser.add_argument(
        "-p",
        "--proxy",
        type=str,
        default=None,
        help="Optional: Global Proxy (ex: http://user:pass@host:port)",
    )
    return parser.parse_args()


def setupAccounts() -> dict:
    accountPath = Path(__file__).resolve().parent / "accounts.json"
    if not accountPath.exists():
        accountPath.write_text(
            json.dumps(
                [
                    {"email": "Your Email 1", "password": "Your Password 1"},
                    {"email": "Your Email 2", "password": "Your Password 2"}
                ], indent=4
            ),
            encoding="utf-8",
        )
        logger.warning('[CREDENTIALS] Accounts credential file "accounts.json" not found.')
        logger.warning('[CREDENTIALS] A new file has been created, please edit with your credentials and save.')
        exit()
    loadedAccounts = json.loads(accountPath.read_text(encoding="utf-8"))
    logger.info(f'[ACCOUNT] No of Total Accounts: {len(loadedAccounts)}!\n')
    return loadedAccounts


def executeBot(currentAccount, notifier: Notifier, args: argparse.Namespace):
    logger.info(
        f'[ACCOUNT] {currentAccount.get("email", "")}',
        tg=True
    )
    with Browser(mobile=False, account=currentAccount, args=args) as desktopBrowser:
        Login(desktopBrowser).login()
        startingPoints = desktopBrowser.utils.getAccountPoints()
        logger.info(
            f"[POINTS] You have {desktopBrowser.utils.formatNumber(startingPoints)} points on your account!",
            tg=True
        )
        DailySet(desktopBrowser).completeDailySet()
        PunchCards(desktopBrowser).completePunchCards()
        MorePromotions(desktopBrowser).completeMorePromotions()
        remainingDesktop, remainingMobile = desktopBrowser.utils.getRemainingSearches()
        if remainingDesktop == remainingMobile  == 0:
            logger.info(
                "[SEARCH] You have already completed today's searches!",
                tg=True
            )
        if remainingDesktop != 0:
            Searches(desktopBrowser).bingSearches(remainingDesktop)
        endPoints = desktopBrowser.utils.getBingAccountPoints()

    if remainingMobile != 0:
        with Browser(
            mobile=True, account=currentAccount, args=args
        ) as mobileBrowser:
            Login(mobileBrowser).login()
            endPoints = Searches(mobileBrowser).bingSearches(remainingMobile)

    logger.info(
        f"[POINTS] You have earned {endPoints - startingPoints} points today!"
    )
    logger.info(
        f"[POINTS] You are now at {endPoints} points!\n"
    )

    notifier.telegram(
        "\n".join(
            [
                "Microsoft Rewards Farmer",
                f"Account: {currentAccount.get('email', '')}",
                    f"Points earned today: {endPoints - startingPoints}",
                f"Total points: {endPoints}",
            ]
        )
    )


if __name__ == "__main__":
    main()