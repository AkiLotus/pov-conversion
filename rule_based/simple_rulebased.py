import sys, re
import numpy as np
np.random.seed(seed=170299)
sys.path.append("../")
import data_handler

corpus = data_handler.TSVCorpus("../data/total.tsv")

def pov_converted(content):
	# KNOWN ISSUE: overlapping cases of the word "her" (possessive or object?)
	# request further context handling
	content = re.sub(r"([^a-z])(@CN's|their|his|her|its)([^a-z])", r"\1your\3", content)
	content = re.sub(r"([^a-z])(@CN@|he|she|they|it)('s)([^a-z])", r"\1\2're\4", content)
	content = re.sub(r"([^a-z])(@CN@|he|she|they|it)( is)([^a-z])", r"\1\2 are\4", content)
	content = re.sub(r"([^a-z])(@CN@|he|she|they|it)([^a-z])(.+?[a-z]+?)(s)?([^a-z])", r"\1you\3\4\6", content)
	content = re.sub(r"([^a-z])(@CN@|him|her|them|it)([^a-z])", r"\1you\3", content)
	content = re.sub(r"([^a-z])(@SCN@'s|i|we)( 'm)([^a-z])", r"\1\2 're\3", content)
	content = re.sub(r"([^a-z])(@SCN@'s|i|we)( am)([^a-z])", r"\1\2 are\3", content)
	content = re.sub(r"([^a-z])(@SCN@'s|i|we)([^a-z])", r"\1they\3", content)
	content = re.sub(r"([^a-z])(@SCN@'s|my|our)([^a-z])", r"\1their\3", content)
	content = re.sub(r"([^a-z])(@SCN@|me|us)([^a-z])", r"\1them\3", content)

	return content

def de_negative(auxiliary):
	if auxiliary == "shan't": return "shall" # special case
	return re.sub(r"n't", "", auxiliary)

greetings = [
	'hi @CN@ , @SCN@ ',
	'hello @CN@ , @SCN@ ',
	'hey @CN@ , @SCN@ ',
]

rule_lists = [
	r"(ask|tell|remind|invite|call|inform|notify|query|remember|send|advise|alert|check|mail|need|update|request|enquire|text|message|contact|write|give|make sure|be sure|warn|email|to|from|with|of) (my |our |the |that )?(friend )?@CN@[^a-z ]?(.+)[^a-z ]?",
	r"let (my |our |the |that )?(friend )?@CN@ know[^a-z ]?(.+)[^a-z ]?", # statement w/ let
	r"(if|whether) @CN@[^a-z ]?(.+)[^a-z ]?", # clear askyn
	r"(do|don't|did|didn't|does|doesn't|will|won't|should|shouldn't|shall|shan't|is|isn't|are|aren't|was|wasn't|were|weren't) (my |our |the |that )?(friend )?@CN@[^a-z ]?(.+)[^a-z ]?", # more askyn
	r"@CN@(.+)" # placeholder
]

for index in range(len(corpus.rows)):
	sentence = str(corpus.get_row(index)["input"])

	response = None

	for re_index in range(len(rule_lists)):
		match_obj = re.search(rule_lists[re_index], sentence)

		if match_obj is not None:
			if re_index == 0:
				verb_used = match_obj.group(1)
				conveyed_content = match_obj.group(4)

				response = greetings[np.random.randint(0, len(greetings))] + verb_used + "s" + " you" + pov_converted(conveyed_content)

			if re_index == 1:
				conveyed_content = match_obj.group(3)

				response = greetings[np.random.randint(0, len(greetings))] + "wants to let you know" + pov_converted(conveyed_content)

			if re_index == 2:
				if_whether = match_obj.group(1)
				conveyed_content = match_obj.group(2)

				response = greetings[np.random.randint(0, len(greetings))] + "wants to know " + if_whether + " you" + pov_converted(conveyed_content)

			if re_index == 3:
				auxiliary = match_obj.group(1)
				conveyed_content = match_obj.group(4)

				response = greetings[np.random.randint(0, len(greetings))] + "wants to know if you " + de_negative(auxiliary) + " " + pov_converted(conveyed_content)

			if re_index == 4:
				conveyed_content = match_obj.group(1)

				response = greetings[np.random.randint(0, len(greetings))] + "tells you" + pov_converted(conveyed_content)

			break
	else:
		response = 'instruction unclear'
	
	print(response)