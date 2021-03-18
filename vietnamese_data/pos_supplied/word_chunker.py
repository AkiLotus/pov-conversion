import sys, re
sys.path.append("../../")
from data_handler import Utilities

tagfile = open(sys.argv[1], "r")

# line = "[('ask', 'VB'), ('@CN@', 'NNP'), ('have', 'VBP'), ('you', 'PRP'), ('found', 'VBN'), ('out', 'RP'), ('about', 'IN'), ('our', 'PRP$'), ('houston', 'NN'), ('trip', 'NN'), ('yet', 'RB')]"

def refined(word):
	return re.sub(r" ?('|’) ?", r"'", word)

def verb_chunking(taglist, tags):
	rule_for_NP = r"((?:V/\d+)(?: E/\d+)*)"

	# print(tags)

	# print(rule_for_NP)

	compounds = re.findall(rule_for_NP, tags)

	index = 0

	new_tags = []

	words = [word for word, _ in taglist]

	for compound in compounds:
		tag_sublist = compound.split()
		start_index = int(tag_sublist[0].split("/")[1])
		end_index = int(tag_sublist[-1].split("/")[1])

		while index < start_index:
			new_tags.append(taglist[index])
			index += 1
		
		compound_word = "_".join(words[start_index:end_index+1])
		new_tags.append((refined(compound_word), "V"))

		index = end_index + 1
	
	while index < len(taglist):
		new_tags.append(taglist[index])
		index += 1
	
	return new_tags

def pronoun_chunking(taglist, tags):
	new_tags = []

	for index in range(taglist):
		if index > 0 and taglist[index][0] == "ấy":
			last_word = new_tags.pop()[0]
			new_tags.append((last_word + "_ấy", "P"))
		else:
			new_tags.append(taglist[index])
	
	return new_tags

while True:
	line = tagfile.readline().strip()
	if len(line) == 0: break

	taglist = Utilities.extract_tag_from_line(line)

	tags = ' '.join(["{}/{}".format(taglist[index][1], index) for index in range(len(taglist))])

	new_tags = verb_chunking(taglist, tags)

	# tags = ' '.join(["{}/{}".format(taglist[index][1], index) for index in range(len(new_tags))])

	# new_tags = negative_aux_chunking(new_tags, tags)

	print(new_tags)