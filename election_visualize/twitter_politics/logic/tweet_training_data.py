import os
import csv

def parse_stanford_data_1(pos_path, neg_path):
	print("Parsing Stanford_1 Database...")
	pos_tweets, neg_tweets = [], []
	for _, _, files in os.walk(pos_path):
		for filename in files:
			f = open(os.path.join(pos_path, filename), 'r')
			pos_tweets.append((f.read(), 'positive'))
			f.close()

	for _, _, files in os.walk(neg_path):
		for filename in files:
			f = open(os.path.join(neg_path, filename), 'r')
			neg_tweets.append((f.read(), 'negative'))
			f.close()
	print("Done.")
	print("....................")
	return pos_tweets, neg_tweets

# NOTE: This function parses data obtained from Sentiment140
def parse_stanford_data_2(filename):
	print("Parsing Stanford_2 Database...")
	pos_tweets, neg_tweets = [], []
	f = open(filename, 'r', encoding='ISO-8859-1')
	reader = csv.reader(f)
	for line in reader:
		if int(line[0]) == 4:
			pos_tweets.append((line[5], 'positive'))
		elif int(line[0]) == 0:
			neg_tweets.append((line[5], 'negative'))
	print("Done.")
	print("....................")
	print(len(pos_tweets), len(neg_tweets))
	return pos_tweets, neg_tweets

def parse_umich_data(filename):
	print("Parsing UMich Database...")
	pos_tweets, neg_tweets = [], []
	f = open(filename, 'r')
	raw_data = [line.split('\t') for line in f]
	for sentiment, text in raw_data:
		if int(sentiment) == 1:
			pos_tweets.append((text, 'positive'))
		else:
			neg_tweets.append((text, 'negative'))
	print("Done.")
	print("---------------------------------------------")
	return pos_tweets, neg_tweets

def create_data_path(relative_path):
    path = os.getcwd()
    if 'instanalyze' not in os.getcwd():
        path = os.path.join(path, 'instanalyze', 'logic')
    for t in relative_path:
        path = os.path.join(path, t)
    return path

def generate_tweet_lists():
	stanford1_pos = create_data_path(['training-data', 'stanford_1', 'pos'])
	stanford1_neg = create_data_path(['training-data', 'stanford_1', 'neg'])
	stanford2 = create_data_path(['training-data', 'stanford_2', 'training.csv'])
	mich = create_data_path(['training-data', 'umich', 'training.txt'])
	pos_tweets_stanford_1, neg_tweets_stanford_1 = parse_stanford_data_1(stanford1_pos, stanford1_neg)
	pos_tweets_stanford_2, neg_tweets_stanford_2 = parse_stanford_data_2(stanford2)
	pos_tweets_umich, neg_tweets_umich = parse_umich_data(mich)
	pos_tweets, neg_tweets = pos_tweets_stanford_1 + pos_tweets_stanford_2 + pos_tweets_umich, neg_tweets_stanford_1 + neg_tweets_stanford_2 + neg_tweets_umich

	if len(pos_tweets) > len(neg_tweets):
		pos_tweets = pos_tweets[:len(neg_tweets)]
	elif len(pos_tweets) < len(neg_tweets):
		neg_tweets = neg_tweets[:len(pos_tweets)]

	return pos_tweets, neg_tweets

