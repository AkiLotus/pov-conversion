from nltk.translate.bleu_score import corpus_bleu, sentence_bleu
from sys import argv
from nltk import word_tokenize

true_output_file = open("../analyzing_development/output.txt", "r")
answer_file = open(argv[1], "r")

true_outputs = []
answers = []

while True:
	out, ans = true_output_file.readline(), answer_file.readline()
	if out == '' or ans == '': break

	print(str(out.split()) + "\n" + str(word_tokenize(ans)) + "\n")
	print('sentence BLEU =', sentence_bleu([word_tokenize(out)], word_tokenize(ans)), "\n")

	true_outputs.append([word_tokenize(out)])
	answers.append(word_tokenize(ans))

	# prompt = input()

print('corpus BLEU =', corpus_bleu(true_outputs, answers))