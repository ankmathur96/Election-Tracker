from django.shortcuts import render
import pickle
# Create your views here.
def is_dem(s):
	dems = ['hillary clinton', 'bernie sanders', 'joe biden', "martin o'malley"]
	if s.lower() in dems:
		return True
	return False
def index(request):
	# with open('pickledic.pickle', 'rb') as dic:
		# results = pickle.load(dic)
	# results are {'state' : (('candidate', score, number_of_pos_tweets, total_number_of_tweets))}
	# with open('breakdowns.pkl', 'r') as breakdowns_file:
	# 	breakdowns = pickle.load(breakdowns_file, breakdowns)
	# with open('state_colors.pkl', 'r') as colors_file:
	# 	state_colors = pickle.load(colors_file, state_colors)
	return render(request, 'twitter-politics/index_3.html', {})