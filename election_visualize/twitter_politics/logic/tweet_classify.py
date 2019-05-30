import json, sys, os, traceback, pickle
import sentiment
from twitter_secrets import google_geo_key
POS_WEIGHT = 1
NEG_WEIGHT = 1
import requests
from collections import defaultdict

# import nltk.data
# try:
# 	sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
# except Exception:
# 	traceback.print_exc()
# 	print('------------------------------------------')
# 	print('continuing execution anyway.')
# 	sent_tokenizer = None
sent_tokenizer = None
# def classify_tweets_ml(tweet_file, classifier=None):
# 	with open(tweet_file, 'rb') as i:
# 		raw_tweets = pickle.load(i)
# 	tweet_texts = set()
# 	tweets = []
# 	for tweet in raw_tweets:
# 		if tweet.text in tweet_texts:
# 			continue
# 		else:
# 			tweet_texts.add(tweet.text)
# 			tweets.append([tweet, 0])
# 	print('Finished file read for', tweet_file)
# 	print('n_tweets_recorded:', len(raw_tweets), '|', 'n_unique_tweets', len(tweet_texts))
# 	print('Beginning classification.')
# 	if classifier is None:
# 		classifier = sentiment.load_classifier()
# 	for tweet_obj in tweets:
# 		tweet = tweet_obj[0]
# 		if sent_tokenizer:
# 			sentences = sent_tokenizer.tokenize(tweet.text)
# 		else:
# 			sentences = [tweet.text]
# 		positives, total = 0, 0
# 		for sentence in sentences:
# 			print(sentence)
# 			for word in sentence.split():
# 				if sentiment.classify_string(word, classifier) == 'positive':
# 					positives += 1
# 				total += 1
# 		score = POS_WEIGHT * positives + NEG_WEIGHT * (total - positives)
# 		print('tweet score:', score)
# 		tweet_obj[1] = score
# 	return tweets

def classify_tweets(tweet_file, scores):
	with open(tweet_file, 'rb') as i:
		raw_tweets = pickle.load(i)
	tweet_texts = set()
	tweets = []
	for tweet in raw_tweets:
		if tweet.text in tweet_texts:
			continue
		else:
			tweet_texts.add(tweet.text)
			tweets.append([tweet, 0])
	print('Finished file read for', tweet_file)
	print('n_tweets_recorded:', len(raw_tweets), '|', 'n_unique_tweets', len(tweet_texts))
	print('Beginning classification.')
	for tweet_obj in tweets:
		tweet = tweet_obj[0]
		if sent_tokenizer:
			sentences = sent_tokenizer.tokenize(tweet.text)
		else:
			sentences = [tweet.text]
		positives, total = 0, 0
		tweet_scores = []
		for sentence in sentences:
			tweet_scores.append(sentiment.analyze_sentence(sentence, scores, POS_WEIGHT, NEG_WEIGHT))
		score = sum(tweet_scores) / len(tweet_scores)
		# print('tweet:', tweet.text)
		# print('tweet score:', score)
		tweet_obj[1] = score
	return tweets

def bin_by_state(candidate, tweets):
	# find the geo-location of a given user. put each tweet in a list with format (state, tweet).
	state_tweets = []
	for tweet in tweets:
		if 'coordinates' in tweet:
			coords = str(tweet['coordinates'][1] + ',' + tweet['coordinates'][0])
			params = {'latlng' : coords, 'key' : google_geo_key}
			url = 'https://maps.googleapis.com/maps/api/geocode/json'
			loc = requests.get(url, params=params).json()['results']
			state = None
			most_acc = loc[0]['address_components']
			for component in most_acc:
				if 'administrative_area_level_1' in component['types']:
					state = component['types']['administrative_area_level_1']['short_name']
					tweet['state'] = state
			if state is None:
				continue
			else:
				state_tweets.append((state, tweet))
	# Then, group by key to get (state, [t1, t2, ...])
	grouped_by_state = defaultdict(state_tweets)
	# once done, go to combine_candidates.py and combine them t
	# on the list for each state, add up the scores for all of the tweets - assign that as the score for the state
	binned_states = {}
	for state in states:
		total_score, n_pos = 0, 0
		for tweet in state[1]:
			if tweet['score'] > 0:
				n_pos += 1
			total_score += tweet['score']
		binned_states[state[0]] = (candidate, total_score, n_pos, len(state[1]))
	return binned_states
	# result is in format {'state' : ('candidate', score, number_of_pos_tweets, total_number_of_tweets)}

def compute_total_score(tweets):
	score = 0
	for tweet_obj in tweets:
		score += tweet_obj[1]
	return score

def compute_candidate_score(candidate, classifier=None):
	print('computing candidate score for:', candidate)
	tagged_tweets = classify_tweets(os.path.join('tweets', candidate + '_tweets.out'), classifier)
	# geo_binned = bin_by_state(candidate, tagged_tweets)
	candidate_score = compute_total_score(tagged_tweets)
	print('candidate score for', candidate, ':', str(candidate_score))
	return candidate_score

if __name__ == "__main__":
	argv = sys.argv[1:]
	candidate = argv[0].lower()
	tagged_tweets = classify_tweets(candidate + '_tweets.out')
	# geo_binned = bin_by_state(candidate, tagged_tweets)
	candidate_score = compute_total_score(tweets)
	with open(os.path.join('tmp', candidate + '_totals.out'), 'w') as candidate_out:
		pickle.dump(candidate_score, candidate_out)

