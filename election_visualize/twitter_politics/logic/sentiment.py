import nltk
import tweet_training_data
import pickle
import os
ROOT = 'twitter-politics'
def create_data_path(relative_path):
    path = os.getcwd()
    if ROOT not in os.getcwd():
        path = os.path.join(path, ROOT, 'logic')
    for t in relative_path:
        path = os.path.join(path, t)
    return path

def clean(s):
    return s.translate(s.maketrans({ord(x) : '' for x in '.,/><!123456789'})).lower()
def canonicalize(l):
    canon_news = []
    for (words, sentiment) in l:
        filtered_words = [clean(x) for x in words.split() if len(x) >= 3]
        canon_news.append((filtered_words, sentiment))
    return canon_news

#canonicalize text

def all_words(l):
    a_words = []
    for (words, sentiment) in l:
        a_words.extend(words)
    return a_words

# This function exists for future proofing. 
# We might want to have a more advanced approach in the future.

def string_to_array(s):
    return s.split()

def extract_word_distribution(l):
    wordlist = nltk.FreqDist(l)
    return wordlist.keys()

def extract_overall_features(doc):
    doc_words = set(doc)
    word_features = extract_word_distribution(doc)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in doc_words)
    return features

def classify_string(s, classifier, debug=False):
    result = classifier.classify(extract_overall_features(string_to_array(s)), debug)
    return result

def test_accuracy(tests, classifier):
    successes = 0
    for test in tests:
        result = classify_string(test[0], classifier)
        if result != test[1]:
            print('FAILED TEST: ', repr(test[0]), 'was supposed to be', test[1], 'but was', result)
        else:
            successes += 1
    print(str(successes/len(tests)), 'success rate')

def create_classifier():
    pos_news, neg_news = tweet_training_data.generate_tweet_lists()
    print('Canonicalize all news.')
    all_news = canonicalize(pos_news + neg_news)
    print('Applying features to all data.')
    training_data = nltk.classify.apply_features(extract_overall_features, all_news)
    # now, we train the classifier.
    print('Starting training')
    classifier = nltk.NaiveBayesClassifier.train(training_data)
    with open('classifier_cache.pickle', 'wb') as classifier_cache:
        pickle.dump(classifier, classifier_cache)
    return classifier

def load_classifier():
    print('loading classifier.')
    if os.path.exists('classifier_cache.pickle'):
        try:
            with open('classifier_cache.pickle', 'rb') as cache_file:
                print('loading cached') 
                classifier = pickle.load(cache_file)
        except Exception:
            classifier = create_classifier()
    else:
        classifier = create_classifier()
    print('classifier loaded.')
    return classifier
def run_tests(classifier):
    test_samples = [('feel happy this morning', 'positive'), ('larry friend', 'positive'), ('not like that man', 'negative'), \
                ('house not great', 'negative'), ('your song annoying', 'negative')]
    test_accuracy(test_samples, classifier)

def generate_scores_from_sentiment_data():
    data_path = create_data_path(['training-data'])
    read_path = os.path.join(data_path, 'sentiments.csv')
    with open(read_path, encoding='utf8') as sentiment_file:
        scores = [line.split(',') for line in sentiment_file]
        scores = {word: float(score.strip()) for word, score in scores}
    write_path = os.path.join(data_path, 'scores.pickle')
    with open(write_path, 'wb') as s_out:
        pickle.dump(scores, s_out)

def load_scores():
    print('loading scores.')
    sent_path = create_data_path(['training-data', 'scores.pickle'])
    with open(sent_path, 'rb') as s_in:
        scores = pickle.load(s_in)
    return scores

def parse_hashtag(htag, words_dict, removed=False):
    #remove hashtag.
    if '_' in htag or '+' in htag:
        return htag.split('_')
    if len(htag) == 0:
        return []
    if not removed:
        htag = htag[1:]
    l_bound, r_bound = 0, len(htag)
    tokens, cur = [], htag
    while (l_bound != r_bound):
        if cur in words_dict and len(cur) > 1:
            tokens.append(cur)
            if r_bound == len(htag):
                return tokens
            htag = htag[r_bound:len(htag)]
            l_bound = 0
            r_bound = len(htag)
        else:
            r_bound -= 1
        cur = htag[l_bound:r_bound]
    if len(htag) != 0:
        tokens.extend(parse_hashtag(htag[1:], words_dict, True))
    return tokens

def clean_and_tokenize(sentence, scores):
    sentence = clean(sentence)
    words = sentence.split()
    clean_sentence = []
    for word in words:
        if word[0] == '#':
            parsed_tokens = parse_hashtag(word, scores)
            if len(parsed_tokens) > 0:
                clean_sentence.extend(parsed_tokens)
        else:
            clean_sentence.append(word)
    return clean_sentence

def test_parse_hashtag():
    scores = load_scores()
    assert parse_hashtag('#coldwinterisbad', scores) == ['cold', 'winter', 'is', 'bad']

def analyze_sentence(sentence, scores, pos_weight=1, neg_weight=1):
    clean_sentence = clean_and_tokenize(sentence, scores)
    sent_scores = []
    for word in clean_sentence:
        if word in scores and scores[word] is not None:
            sent_scores.append(scores[word])
    if len(sent_scores) == 0:
        return 0
    sum_score = sum([x * pos_weight for x in sent_scores if x > 0]) + sum([x * neg_weight for x in sent_scores if x < 0])
    return sum_score/len(sent_scores)

def analyze_sentence_ml(sentence, classifier, scores):
    clean_sentence = clean_and_tokenize(sentence, scores)
    result = classify_array(clean_sentence, classifier)
    print(result)
# pos_news = [('I love this car', 'positive'), ('This view is amazing', 'positive'), \
#           ('I feel great this morning', 'positive'), ('He is my best friend', 'positive')]
# neg_news = [('I do not like this car', 'negative'), ('This view is horrible', 'negative'), \
#           ('I feel tired this morning.', 'negative'), ('He is an enemy of mine', 'negative')]
if __name__ == "__main__":
    classifier = load_classifier()

