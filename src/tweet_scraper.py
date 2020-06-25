from tweepy import OAuthHandler, Cursor, API
import json
import pandas as pd
import time

import twitter_credentials as tc

class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.twitter_user = twitter_user

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user, tweet_mode="extended").items(num_tweets):
            if (not tweet.retweeted) and ('RT @' not in tweet.full_text):
                tweets.append(tweet.full_text)
        return tweets


class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        auth = OAuthHandler(tc.CONSUMER_KEY, tc.CONSUMER_SECRET)
        auth.set_access_token(tc.ACCESS_TOKEN, tc.ACCESS_TOKEN_SECRET)
        return auth

def get_right_tweets(num):
    right_tweets = []
    for user in pd.read_csv('../data/right_account_list.csv').right:
        twitter_client = TwitterClient(user)
        try:
            tweets = twitter_client.get_user_timeline_tweets(num)
            for tweet in tweets:
                right_tweets.append(tweet)
                print(tweet)
        except:
            print("Failed to get tweets for: "+user)
        time.sleep(10)
    right_df = pd.DataFrame(right_tweets, columns=["tweets"])
    right_df.to_csv('../data/right_tweets.csv')

def get_left_tweets(num):
    left_tweets = []
    for user in pd.read_csv('../data/left_account_list.csv').left:
        twitter_client = TwitterClient(user)
        try:
            tweets = twitter_client.get_user_timeline_tweets(num)
            for tweet in tweets:
                left_tweets.append(tweet)
                print(tweet)
        except:
            print("Failed to get tweets for: "+user)
        time.sleep(10)
    left_df = pd.DataFrame(left_tweets, columns=["tweets"])
    left_df.to_csv('../data/left_tweets.csv')

if __name__=='__main__':
    count = 1000
    get_right_tweets(count)
    #get_left_tweets(count)
    pass

