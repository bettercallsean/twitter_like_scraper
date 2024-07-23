import json
import os
import time
import datetime

import pyotp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from pyvirtualdisplay import Display

import settings

CURRENT_TIME = datetime.datetime.now()
LIKED_TWEETS_FOLDER = os.path.join(
    settings.CURRENT_DIRECTORY, "tweets", f"{CURRENT_TIME:%d-%m-%Y}"
)
MOST_RECENT_LIKED_TWEET_FILE = os.path.join(
    settings.CURRENT_DIRECTORY, "most_recent_liked_tweet.txt"
)


def parse_liked_tweets(username: str) -> None:
    if not os.path.exists(LIKED_TWEETS_FOLDER):
        os.makedirs(LIKED_TWEETS_FOLDER)

    most_recent_liked_tweet = ""
    if os.path.exists(MOST_RECENT_LIKED_TWEET_FILE):
        with open(MOST_RECENT_LIKED_TWEET_FILE, "r") as f:
            most_recent_liked_tweet = f.read()

    driver.get(f"https://twitter.com/{username}/likes")

    name_header = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".r-1gn8etr"))
    )

    driver.execute_script(
        """
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """,
        name_header,
    )

    tweets = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'section[class="css-175oi2r"]')
        )
    )

    tweets = {}
    last_stored_tweet_id = ""
    most_recent_liked_tweet_found = False

    while not most_recent_liked_tweet_found:
        liked_tweets = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')

        last_tweet_found = False
        for tweet in liked_tweets:
            if (
                tweet.id != last_stored_tweet_id
                and not last_tweet_found
                and last_stored_tweet_id != ""
            ):
                continue

            if tweet.id == last_stored_tweet_id:
                last_tweet_found = True
                continue

            soup = BeautifulSoup(tweet.get_attribute("outerHTML"), "html.parser")
            tweet_link = soup.find_all("a")[3].attrs["href"]

            if tweet_link == most_recent_liked_tweet and most_recent_liked_tweet != "":
                most_recent_liked_tweet_found = True
                break

            time.sleep(1)
            tweet.screenshot(f"{LIKED_TWEETS_FOLDER}/{tweet.id}.png")
            time.sleep(1)
            tweets[tweet_link] = tweet.id
            last_stored_tweet_id = tweet.id

            if most_recent_liked_tweet == "":
                most_recent_liked_tweet_found = True
                break

    create_tweet_files(tweets)


def login_to_twitter(username: str, password: str, otp_key: str) -> None:
    driver.get("https://twitter.com/")

    cookie_button = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "button.r-18kxxzh:nth-child(2)")
        )
    )
    cookie_button[0].click()

    driver.get("https://twitter.com/i/flow/login")

    username_field = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[autocomplete=username]")
        )
    )
    username_field.send_keys(username)

    login_button = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[role=button].r-13qz1uu"))
    )
    login_button.click()

    password_field = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[type=password]"))
    )
    password_field.send_keys(password)

    login_button = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid*=Login_Button]"))
    )
    login_button.click()

    time.sleep(2)

    otp_field = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[data-testid=ocfEnterTextTextInput]")
        )
    )

    if otp_key is not None:
        totp = pyotp.TOTP(otp_key)
        otp = totp.now()
        otp_field.send_keys(otp)
        otp_field.send_keys(Keys.ENTER)

    direct_message_link = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[data-testid=AppTabBar_DirectMessage_Link]")
        )
    )


def create_tweet_files(tweets: dict) -> None:
    if len(tweets) > 0:
        with open(MOST_RECENT_LIKED_TWEET_FILE, "w") as f:
            f.write(list(tweets)[0])

        with open(f"{LIKED_TWEETS_FOLDER}/{CURRENT_TIME:%d-%m-%Y}.json", "w+") as f:
            result = json.dumps(tweets)
            f.write(result)


if __name__ == "__main__":
    display = Display(visible=0, size=(1200, 675))
    display.start()

    options = Options()
    options.add_argument("-headless")
    options.preferences.update({
        "javascript.enabled": True,
    })
    service = webdriver.FirefoxService(executable_path=settings.GECKODRIVER_LOCATION)
    driver = webdriver.Firefox(service=service, options=options)
    wait = WebDriverWait(driver, 20)

    login_to_twitter(settings.USERNAME, settings.PASSWORD, settings.OTP_KEY)
    parse_liked_tweets(settings.USERNAME)

    driver.close()
    display.stop()
