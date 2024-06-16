#!/usr/bin/python3
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
SCREENSHOTS_FOLDER = os.path.join(settings.CURRENT_DIRECTORY, "screenshots", f"{CURRENT_TIME:%d-%m-%Y}")
LIKED_TWEETS_FOLDER = os.path.join(settings.CURRENT_DIRECTORY, "tweets")


def parse_liked_tweets(username: str) -> None:
    if not os.path.exists(SCREENSHOTS_FOLDER):
        os.mkdir(SCREENSHOTS_FOLDER)

    if not os.path.exists(LIKED_TWEETS_FOLDER):
        os.mkdir(LIKED_TWEETS_FOLDER)

    most_recent_liked_tweet = ""
    if os.path.exists("most_recent_liked_tweet.txt"):
        with open("most_recent_liked_tweet.txt", "r") as f:
            most_recent_liked_tweet = f.read()


    driver.get(f"https://twitter.com/{username}/likes")

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

            tweet.screenshot(f"{SCREENSHOTS_FOLDER}/{tweet.id}.png")
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
            (By.XPATH, '//*[@id="layers"]/div/div[1]/div/div/div/div[2]/button[2]')
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
        with open("most_recent_liked_tweet.txt", "w") as f:
            f.write(list(tweets)[0])

        with open(f"{LIKED_TWEETS_FOLDER}/{CURRENT_TIME:%d-%m-%Y}.json", "w+") as f:
            result = json.dumps(tweets)
            f.write(result)


if __name__ == "__main__":
    display = Display(visible=0, size=(600, 800))
    display.start()

    options = Options()
    options.add_argument("-headless")
    service = webdriver.FirefoxService(executable_path="/usr/local/bin/geckodriver")
    driver = webdriver.Firefox(service=service, options=options)
    wait = WebDriverWait(driver, 20)

    login_to_twitter(settings.USERNAME, settings.PASSWORD, settings.OTP_KEY)
    parse_liked_tweets(settings.USERNAME)

    driver.close()
    display.stop()
