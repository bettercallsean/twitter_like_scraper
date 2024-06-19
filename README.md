# twitter_like_scraper
A Python script that uses Selenium to log into your Twitter account and scrape your most recent liked tweets. Everything is ran locally so you don't need to worry about me stealing your passwords :)

## Usage

Create a `creds.env` file in the root directory, with the following keys
```
USERNAME="yourusername"
PASSWORD="yourpassword"
```

If you have two-factor authentication enabled on your account, add the following to the creds file as well
```
OTP_KEY="yourotpkey"
```
You will need to get the OTP Secret key from whatever authenticator app you use.

After you have created this file, run the following from the terminal
```
pip install -r requirements.txt
```

You can then run the script as you normally would either via the terminal or using an IDE.

When you run the script for the first time, it will simply save the most recent liked tweet URL in `most_recent_liked_tweet.txt` and not any . 
This is used as a base point for the next time the script runs, to see what tweets have been liked since this tweet.
The script will update `most_recent_liked_tweet.txt` every time it runs with the most recent tweet.

## What is stored?
When the script is run, it will save the tweet URL and a screenshot in a folder with the current date. A json file will be created with the current date as its name (e.g. `19-06-2024.json`) and will contain a dictionary mapping the Tweet URLs to their respective screenshots.
The contents of the file will look something like this
```
{
  "/tristandross/status/1802266798529626371": "54fe2855-9049-4f46-9da3-f8eadf1c554c",
  "/Ursen_/status/1802124405440454706": "11479d3e-747f-4c72-b520-bfce382efe4b",
  "/pattymo/status/1802000937180975575": "1845cbf1-e832-4fc0-b96d-a1c13459cc14"
}
```
The key is the path to the tweet. Appending this to `twitter.com` will take you to the tweet in question. The value is the name of the screenshot for that particular tweet.

## Limitations
From my experience with developing and testing this, if you run the script too many times within a certain time frame (about 10-20 minutes), Twitter will prevent you from logging in and will display a 'Suspicious login prevented' warning (your results may vary).
You can still use Twitter like normal if you're still logged in on your phone, laptop etc. but you just won't be able to sign-in for a little while.
