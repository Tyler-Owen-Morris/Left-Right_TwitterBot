from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json

import twitter_credentials as tc

class StdOutListener (StreamListener):

    def on_data(self, data):
        tweet = json.loads(data)
        #print(data)
        #print(str(tweet)+'\n')
        print(tweet['user']['name']+'\n')
        
        try:
            print(tweet['retweeted_status']['extended_tweet']['full_text']+"\n ************************")
        except:
            print(tweet['text']+"\n ***************************************")
        return True

    def on_error(self, status):
        print(status)


if __name__ == "__main__":

    listener = StdOutListener()
    auth = OAuthHandler(tc.CONSUMER_KEY, tc.CONSUMER_SECRET)
    auth.set_access_token(tc.ACCESS_TOKEN, tc.ACCESS_TOKEN_SECRET)

    stream = Stream(auth,listener)

    stream.filter(track=["$flo", "flo"])