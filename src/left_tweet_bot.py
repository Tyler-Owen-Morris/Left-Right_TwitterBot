from tweepy import OAuthHandler, Cursor, API
import json
import pandas as pd
import time
from random import randint

import twitter_credentials_left as tc

auth = OAuthHandler(tc.CONSUMER_KEY, tc.CONSUMER_SECRET)
auth.set_access_token(tc.ACCESS_TOKEN, tc.ACCESS_TOKEN_SECRET)
api = API(auth, wait_on_rate_limit=True)

gen_ts = pd.read_csv('../data/gen_tweets2.csv')

def do_bot_things():
    while True:
        tweet = gen_ts.tweets.sample(1).values[0]
        print("Preparing to tweet this nugget of genius:\n"+tweet)
        api.update_status(tweet)
        sleep_time = (35*60) + randint(-20,20)*60
        print("Going to sleep for "+str(sleep_time/60)+" minutes")
        time.sleep(sleep_time)

if __name__ == "__main__":
    do_bot_things()