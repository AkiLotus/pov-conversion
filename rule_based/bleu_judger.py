from nltk.translate.bleu_score import corpus_bleu, sentence_bleu
from sys import argv

true_output_file = open("../analyzing_development/output.txt", "r")
answer_file = open(argv[1], "r")

true_outputs = []
answers = []

while True:
	out, ans = true_output_file.readline(), answer_file.readline()
	if out == '' or ans == '': break

	print(str(out.split()) + "\n" + str(ans.split()) + "\n")
	print('sentence BLEU =', sentence_bleu([out.split()], ans.split()), "\n")

	true_outputs.append([out.split()])
	answers.append(ans.split())

	# prompt = input()

print('corpus BLEU =', corpus_bleu(true_outputs, answers))