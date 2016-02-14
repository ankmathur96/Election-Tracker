from states import state_list, candidate_list
import os
def generate_state_view_info(state_bins):
	state_colors = {}
	for state in state_bins:
		dem_score, rep_score = 0, 0
		for candidate in state_bins[state]:
			print(candidate[0])
			if is_dem(candidate[0]):
				dem_score += candidate[1]
			else:
				rep_score += candidate[1]
		if dem_score > rep_score:
			state_colors[state] = ('#0066FF', '#0000FF')
		else:
			state_colors[state] = ('#FF3300', '#CC0000')
	for state in results:
		breakdowns[state] = ''.join([x[0] + ' : ' + str(x[1]) + '%' + ' based on ' + str(x[2]) + ' sample points.<br/>' for x in results[state]])
	with open('breakdowns.pkl', 'w') as breakdowns_file:
		pickle.dump(breakdowns_file, breakdowns)
	with open('state_colors.pkl', 'w') as colors_file:
		pickle.dump(colors_file, state_colors)

if __name__ == "__main__":
	for c in candidate_list:
		f_name = c + '_totals.out'
		try:
			with open(os.path.join('tmp', f_name), 'r') as c_file:
				c_state_bins = pickle.load(c_file)
		except Exception:
			print('*' *  20)
			print('candidate', c, 'file not found.')
			pass
	# all the dictionaries must have the same keys. combine them all.
	combined_state_info = 
	# then, generate the view.
	generate_state_view_info(combined_state_info)



