from nltk.translate.meteor_score import single_meteor_score
import numpy as np
from sys import argv

true_output_file = open("../analyzing_development/output.txt", "r")
answer_file = open(argv[1], "r")

true_outputs = []
answers = []

meteors = []

while True:
	out, ans = true_output_file.readline(), answer_file.readline()
	if out == '' or ans == '': break

	met_score = single_meteor_score(out, ans)

	print(out + ans)
	print('sentence METEOR =', met_score, "\n")

	true_outputs.append(out)
	answers.append(ans)

	meteors.append(met_score)

	# prompt = input()

print('corpus METEOR =', np.average(np.array(meteors)))