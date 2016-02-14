from tweet_classify import compute_candidate_score
from util_lists import candidate_list
from twitter_stream import run_listener
from twitter_secrets import pub_publish_key, pub_sub_key, pub_secret_key
import sentiment
import time
from pubnub import Pubnub

UPDATE_WAIT_TIME = 1 # seconds
results = []
# load this here so the classifier stays alive.
# classifier = sentiment.load_classifier()
scores = sentiment.load_scores()
pubnub = Pubnub(publish_key=pub_publish_key, subscribe_key=pub_sub_key)
def error(e):
	print(e)

while 1:
	print(candidate_list)
	results = {}
	for candidate in candidate_list:
		run_listener(candidate)
		print('finished running listener for', candidate)
		results[candidate] = compute_candidate_score(candidate, scores)
		# results[candidate] = compute_candidate_score(candidate, classifier)
	# push results
	pubnub.publish('chart-data', {"eon" : results}, callback=lambda e: print('successful push'), error=error)
	print('pushed results')
	# wait for 1 minute
	print('going to sleep for', str(UPDATE_WAIT_TIME), 'seconds.')
	time.sleep(UPDATE_WAIT_TIME)
