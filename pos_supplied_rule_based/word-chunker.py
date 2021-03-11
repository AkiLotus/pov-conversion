import sys, re
sys.path.append("../")
from data_handler import Utilities

tagfile = open(sys.argv[1], "r")

# line = "[('ask', 'VB'), ('@CN@', 'NNP'), ('have', 'VBP'), ('you', 'PRP'), ('found', 'VBN'), ('out', 'RP'), ('about', 'IN'), ('our', 'PRP$'), ('houston', 'NN'), ('trip', 'NN'), ('yet', 'RB')]"

def refined(word):
	return re.sub(r" ?('|’) ?", r"'", word)

def NP_chunking(taglist, tags):
	rule_for_NP = r"([^A-Z|^](?:(?:CD|DT|PRP\$)/\d+ )*(?:(?:RBS?R?/\d+ )*JJS?R?/\d+ )*(?:(?:NNP?S?|FW|CD|SYM|POS)/\d+ )*(?:(?:NNP?S?|FW|CD|SYM)/\d+)(?: POS/\d+)?)"

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
		
		compound_word = " ".join(words[start_index:end_index+1])

		if "@CN@" in words[start_index:end_index+1]:
			split_position = words[start_index:end_index+1].index("@CN@") + start_index
			compound_1 = " ".join(words[start_index:split_position+1])
			compound_2 = " ".join(words[split_position+1:end_index+1])
			new_tags.append((refined(compound_1), "NP"))
			if compound_2 != "": new_tags.append((refined(compound_2), "NP"))
		else:
			new_tags.append((refined(compound_word), "NP"))

		index = end_index + 1
	
	while index < len(taglist):
		new_tags.append(taglist[index])
		index += 1
	
	return new_tags

def negative_aux_chunking(taglist, tags):
	rule_for_aux = r"([^A-Z|^](?:MD|V[A-Z]*?)/\d+ RB/\d+?)"

	# print(tags)

	# print(rule_for_NP)

	compounds = re.findall(rule_for_aux, tags)

	index = 0

	new_tags = []

	words = [word for word, _ in taglist]

	for compound in compounds:
		tag_sublist = compound.split()
		start_index = int(tag_sublist[0].split("/")[1])
		end_index = int(tag_sublist[-1].split("/")[1])

		if words[end_index] != "not":
			while index <= end_index:
				new_tags.append(taglist[index])
				index += 1
			continue

		while index < start_index:
			new_tags.append(taglist[index])
			index += 1
		
		auxiliary = words[start_index]

		neg_auxiliary = auxiliary + "n't"

		if auxiliary == "can":
			neg_auxiliary = "can't"
		if auxiliary == "shall":
			neg_auxiliary = "shan't"

		new_tags.append((refined(neg_auxiliary), "VAN"))

		index = end_index + 1
	
	while index < len(taglist):
		new_tags.append(taglist[index])
		index += 1
	
	return new_tags

while True:
	line = tagfile.readline().strip()
	if len(line) == 0: break

	taglist = Utilities.extract_tag_from_line(line)

	tags = ' '.join(["{}/{}".format(taglist[index][1], index) for index in range(len(taglist))])

	new_tags = NP_chunking(taglist, tags)

	tags = ' '.join(["{}/{}".format(taglist[index][1], index) for index in range(len(new_tags))])

	new_tags = negative_aux_chunking(new_tags, tags)

	print(new_tags)