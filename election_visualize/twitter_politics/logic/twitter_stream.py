import time
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from tweepy.api import API
from tweepy.models import Status
import pickle
import sys
import urllib
import os
from twitter_secrets import access_token, access_token_secret, consumer_key, consumer_secret
import json

GEO_ACTIVE = False
class NormalListener(StreamListener):
    LIMIT_BACKOFF = 1
    ERROR_BACKOFF = 1
    def __init__(self, api, candidate, start_time, time_limit=60, tweets_needed=30):
        self.time = start_time
        self.limit = time_limit
        self.candidate = candidate
        self.tweets_needed = tweets_needed
        self.recorded = 0
        self.api = api
        self.recorded_tweets = []
    # def on_data(self, data):
    #     return super(NormalListener, self).on_data(data)
    # def on_data(self, data):
    #   data = json.loads(raw_data)
    #   if (time.time() - self.time) > self.limit:
    #       return False
 #        if 'in_reply_to_status_id' in data:
 #            status = Status.parse(self.api, data)
 #            if self.on_status(status) is False:
 #                return False
 #        elif 'delete' in data:
 #            delete = data['delete']['status']
 #            if self.on_delete(delete['id'], delete['user_id']) is False:
 #                return False
 #        elif 'event' in data:
 #            status = Status.parse(self.api, data)
 #            if self.on_event(status) is False:
 #                return False
 #        elif 'direct_message' in data:
 #            status = Status.parse(self.api, data)
 #            if self.on_direct_message(status) is False:
 #                return False
 #        elif 'friends' in data:
 #            if self.on_friends(data['friends']) is False:
 #                return False
 #        elif 'limit' in data:
 #            if self.on_limit(data['limit']['track']) is False:
 #                return False
 #        elif 'disconnect' in data:
 #            if self.on_disconnect(data['disconnect']) is False:
 #                return False
 #        elif 'warning' in data:
 #            if self.on_warning(data['warning']) is False:
 #                return False
 #        else:
 #            logging.error("Unknown message type: " + str(raw_data))
    def on_limit(self, status):
        print('being rate limited:', status)
        time.sleep(LIMIT_BACKOFF)
        LIMIT_BACKOFF *= 2
        return False
    def on_status(self, status):
        if (time.time() - self.time) < self.limit:
            print('record hit', self.recorded)
            try:
                self.recorded_tweets.append(status)
                self.recorded += 1
                return True
            except BaseException as e:
                print('failed ondata,', str(e))
                time.sleep(5)
                return False
        else:
            with open(os.path.join('tweets', self.candidate + '_tweets.out'), 'wb') as candidate_file:
                pickle.dump(self.recorded_tweets, candidate_file)
            return False
 
    def on_error(self, status):
        if status == 420:
            print "RATE LIMIT AGAIN"
            if ERROR_BACKOFF <= 16:
                time.sleep(BACKOFF * 60)
                ERROR_BACKOFF *= 2
                return True
            else:
                return False
        print('error:', status)
        with open(os.path.join('tweets', self.candidate + '_tweets.out'), 'wb') as candidate_file:
            pickle.dump(self.recorded_tweets, candidate_file)
        return False

# unfortunately, it looks like most tweets just don't have the geo data in them. rip.
class GeoListener(StreamListener):
    #allows you to set a huge timeout and try to force only tweets with geo tag included.
    def __init__(self, candidate, start_time, time_limit=60, tweets_needed=30):
        self.api = api
        self.time = start_time
        self.limit = time_limit
        self.candidate = candidate
        self.tweets_needed = tweets_needed
        self.recorded = 0

    def on_data(self, data):
        while (time.time() - self.time) < self.limit and self.recorded < self.tweets_needed:
            try:
                tweet = json.loads(data)
                if tweet['coordinates'] is None:
                     print(tweet)
                     return True
                print('record hit', self.recorded)
                with open(os.path.join('tweets', self.candidate + '_tweets.out'), 'ab') as candidate_file:
                    output_str = pickle.dumps(tweet)
                    candidate_file.write(output_str)
                    candidate_file.close()
                    self.recorded += 1
                    return True
            except BaseException as e:
                print('failed ondata,', str(e))
                time.sleep(5)
                pass 
        return
 
    def on_error(self, status):
        print(status)

def run_listener(candidate):
    keyword_list = [candidate]
    auth = OAuthHandler(consumer_key, consumer_secret) #OAuth object
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth)
    start_time = time.time()
    if GEO_ACTIVE:
        listener_object = GeoListener(candidate, start_time, time_limit=1000000)
    else:
        listener_object = NormalListener(api, candidate, start_time, 10)
    twitterStream = Stream(auth = api.auth, listener=listener_object) #initialize Stream object with a time out limit
    print('now listening for', candidate,'...')
    twitterStream.filter(track=keyword_list, languages=['en'])  #call the filter method to run the Stream Object

if __name__ == "__main__":
    argv = sys.argv[1:]
    run_listener(argv[0].lower())