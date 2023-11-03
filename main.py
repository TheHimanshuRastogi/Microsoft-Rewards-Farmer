"""
This is a module docstring
"""


import sys
import json
import logging
import argparse
from pathlib import Path
import logging.handlers as handlers

from src.notifier import Notifier
from src.constants import VERSION
from src.loggingColoredFormatter import ColoredFormatter
from src import Browser, DailySet, Login, MorePromotions, PunchCards, Searches


def main():
    setupLogging()
    args = argumentParser()
    notifier = Notifier(args)
    loadedAccounts = setupAccounts()
    for currentAccount in loadedAccounts:
        try:
            executeBot(currentAccount, notifier, args)
        except Exception as e:
            logging.exception(f"{e.__class__.__name__}: {e}")


def setupLogging():
    format = "%(asctime)s [%(levelname)s] %(message)s"
    terminalHandler = logging.StreamHandler(sys.stdout)
    terminalHandler.setFormatter(ColoredFormatter(format))

    (Path(__file__).resolve().parent / "logs").mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format=format,
        handlers=[
            handlers.TimedRotatingFileHandler(
                "logs/activity.log",
                when="midnight",
                interval=1,
                backupCount=2,
                encoding="utf-8",
            ),
            terminalHandler,
        ],
    )


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
    parser.add_argument(
        "-t",
        "--telegram",
        metavar=("TOKEN", "CHAT_ID"),
        nargs=2,
        type=str,
        default=None,
        help="Optional: Telegram Bot Token and Chat ID (ex: 123456789:ABCdefGhIjKlmNoPQRsTUVwxyZ 123456789)",
    )
    parser.add_argument(
        "-d",
        "--discord",
        type=str,
        default=None,
        help="Optional: Discord Webhook URL (ex: https://discord.com/api/webhooks/123456789/ABCdefGhIjKlmNoPQRsTUVwxyZ)",
    )
    return parser.parse_args()

def setupAccounts() -> dict:
    accountPath = Path(__file__).resolve().parent / "accounts.json"
    if not accountPath.exists():
        accountPath.write_text(
            json.dumps(
                [{"email": "Your Email", "password": "Your Password"}], indent=4
            ),
            encoding="utf-8",
        )
        noAccountsNotice = """
    [ACCOUNT] Accounts credential file "accounts.json" not found.
    [ACCOUNT] A new file has been created, please edit with your credentials and save.
    """
        logging.warning(noAccountsNotice)
        exit()
    loadedAccounts = json.loads(accountPath.read_text(encoding="utf-8"))
    return loadedAccounts


def executeBot(currentAccount, notifier: Notifier, args: argparse.Namespace):
    logging.info(
        f'[ACCOUNT] {currentAccount.get("email", "")}'
    )
    with Browser(mobile=False, account=currentAccount, args=args) as desktopBrowser:
        Login(desktopBrowser).login()
        startingPoints = desktopBrowser.utils.getAccountPoints()
        logging.info(
            f"[POINTS] You have {desktopBrowser.utils.formatNumber(startingPoints)} points on your account!"
        )
        DailySet(desktopBrowser).completeDailySet()
        PunchCards(desktopBrowser).completePunchCards()
        MorePromotions(desktopBrowser).completeMorePromotions()
        remainingDesktop, remainingMobile = desktopBrowser.utils.getRemainingSearches()
        if remainingDesktop == remainingMobile  == 0:
            logging.info(
                "[SEARCH] You have already completed today's searches!"
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

    logging.info(
        f"[POINTS] You have earned {endPoints - startingPoints} points today!"
    )
    logging.info(
        f"[POINTS] You are now at {endPoints} points!\n"
    )

    notifier.send(
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
