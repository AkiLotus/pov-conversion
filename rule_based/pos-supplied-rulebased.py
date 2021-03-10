import sys, re, json
import numpy as np
np.random.seed(seed=170299)
sys.path.append("../")
import data_handler
from nltk import word_tokenize
from nltk.tag.stanford import StanfordPOSTagger
from os.path import expanduser

corpus = data_handler.TSVCorpus("../data/test.tsv")

home = expanduser("~")
_path_to_model = home + '/stanford-postagger/models/english-bidirectional-distsim.tagger'
_path_to_jar = home + '/stanford-postagger/stanford-postagger.jar'
st = StanfordPOSTagger(model_filename=_path_to_model, path_to_jar=_path_to_jar)

irregular_verbs = json.loads(open("../resources/english-irregular-verbs.json", "r").read())

rule_for_NP = r"([^A-Z|^](?:(?:CD|DT|PRP\$)/\d+ )*(?:(?:RBS?R?/\d+ )*JJS?R?/\d+ )*(?:(?:NNP?S?|FW|CD|SYM|POS)/\d+ )*(?:(?:NNP?S?|FW|CD|SYM)/\d+))"

def de_negative(auxiliary):
	if auxiliary == "shan't": return "shall" # special case
	return re.sub(r"n't", "", auxiliary)

def singular_3rd_person(verb):
	if verb == "be": return "is"
	if verb == "have": return "has"

	verb = re.sub(r"([^aeiou])y$", r"\1i", verb)
	verb = re.sub(r"(i|ch|s|sh|x|z)$", r"\1e", verb)

	return (verb + "s")

def past_verb(verb):
	if verb in irregular_verbs:
		return irregular_verbs[verb][0]['2'][np.random.randint(0, len(irregular_verbs[verb][0]['2']))]

	if len(verb) and verb[-1] != "e": verb += "e"
	return (verb + "d")

def preprocess(sentence):
	sentence = sentence.replace("’", "'")

	sentence = re.sub(r"^([^(@CN@)]*) ?,? ?(please|kindly|gently|honou?red|honou?rly) ?,? ?", r"\1", sentence)
	sentence = re.sub(r"^(hi|hello|hey) ?,? ?", r"", sentence)
	sentence = re.sub(r"^([^(@CN@)]*) ?,? ?(can|could|may|might|will|would) you ?,? ?", r"\1", sentence)
	sentence = re.sub(r"^[a-z][^a-z]", r"", sentence)
	sentence = re.sub(r"\"([a-z.\?!].+[a-z.\?!])\"", r"\1", sentence)
	sentence = re.sub(r" ?,? ?i (want|need|order|command) (you )?to ?,? ?", r"", sentence)
	sentence = re.sub(r"^(ask?[a-z]?|aks?[a-z]?|sak?[a-z]?)", r"ask", sentence)

	sentence = re.sub(r" ?'m", r" am", sentence)
	sentence = re.sub(r" ?'re", r" are", sentence)
	sentence = re.sub(r" ?'ve", r" have", sentence)
	sentence = re.sub(r" ?'ll", r" will", sentence)
	sentence = re.sub(r" ?'d", r" would", sentence)
	sentence = re.sub(r" ?can't", r" can not", sentence)
	sentence = re.sub(r" ?won't", r" will not", sentence)
	sentence = re.sub(r" ?shan't", r" shall not", sentence)
	sentence = re.sub(r" ?n't", r" not", sentence)

	sentence = re.sub(r",? i ", r" I ", sentence)
	sentence = "can you " + sentence

	return sentence

def tokenizer(sentence):
	temporal_token = ""
	new_tokens = []

	for token in word_tokenize(sentence):
		if token == "@":
			temporal_token += token
			if temporal_token != "@":
				new_tokens.append(temporal_token)
				temporal_token = ""
		elif temporal_token != "":
			temporal_token += token
		else:
			new_tokens.append(token)
	
	return new_tokens

def pos_tagger(tokenized_sentence):
	raw_tags = st.tag(tokenized_sentence)

	tags = []
	first_CN, nearest_VB_before_CN, index = -1, -1, 0

	for word, tag in raw_tags:
		if word == "@CN@" or word == "@SCN@":
			tags.append((word, "NNP"))
			if word == "@CN@" and first_CN == -1:
				first_CN = index
		else:
			if tag == "VB" and first_CN == -1:
				nearest_VB_before_CN = index
			tags.append((word, tag))
		
		index += 1

	if nearest_VB_before_CN == -1: return tags[2:] # solely remove "can you"
	return tags[nearest_VB_before_CN:] # remove everything before first @CN@

def noun_chunker(pos_tags):
	if pos_tags is None: return None

	tags = ' '.join(["{}/{}".format(pos_tags[index][1], index) for index in range(len(pos_tags))])

	# print(tags)

	# print(rule_for_NP)

	compounds = re.findall(rule_for_NP, tags)

	index = 0

	new_tags = []

	words = [word for word, _ in pos_tags]

	for compound in compounds:
		tag_sublist = compound.split()
		start_index = int(tag_sublist[0].split("/")[1])
		end_index = int(tag_sublist[-1].split("/")[1])

		while index < start_index:
			new_tags.append(pos_tags[index])
			index += 1
		
		compound_word = " ".join(words[start_index:end_index+1])

		if "@CN@" in words[start_index:end_index+1]:
			split_position = words[start_index:end_index+1].index("@CN@") + start_index
			compound_1 = " ".join(words[start_index:split_position+1])
			compound_2 = " ".join(words[split_position+1:end_index+1])
			new_tags.append((compound_1, "NP"))
			if compound_2 != "": new_tags.append((compound_2, "NP"))
		else:
			new_tags.append((compound_word, "NP"))

		index = end_index + 1
	
	while index < len(pos_tags):
		new_tags.append(pos_tags[index])
		index += 1

	return new_tags

def check_yesno(content):
	# check if the conveying clause is a yes-no question or not
	# very simple one, catch the auxiliary and assume the subject following it consists of one token only
	# (will miss cases like "bob's door" or "alice's dress", blah)

	# print(content)

	# match_obj = re.search(r"^(^|[^a-z]+)?(shan't|do|does|did|is|are|was|were|will|shall|would|should|may|might|can|could|have|has|had)(n't)? (@CN@'s|his|her|its|their|our|your|my )?(@CN@|[a-z]+)([^a-z]|$)(.*)$", content)
	# if match_obj is not None:
	# 	match_obj = match_obj.groups("")
	# 	content = match_obj[0] + "whether " + match_obj[3] + match_obj[4] + " " + match_obj[1] + match_obj[2] + match_obj[5] + match_obj[6]
	# # print(content)

	# match_obj = re.search(r"^(^|[^a-z]+)?whether (@CN@'s|his|her|its|their|our|your|my )?(@CN@|[a-z]+) do ([a-z]+)([^a-z]|$)(.*)$", content)
	# if match_obj is not None:
	# 	match_obj = match_obj.groups("")
	# 	content = match_obj[0] + "whether " + match_obj[1] + match_obj[2] + " " + match_obj[3] + match_obj[4] + match_obj[5]
	# # print(content)

	# match_obj = re.search(r"^(^|[^a-z]+)?whether (@CN@'s|his|her|its|their|our|your|my )?(@CN@|[a-z]+) does ([a-z]+)([^a-z]|$)(.*)$", content)
	# if match_obj is not None:
	# 	match_obj = match_obj.groups("")
	# 	content = match_obj[0] + "whether " + match_obj[1] + match_obj[2] + " " + singular_3rd_person(match_obj[3]) + match_obj[4] + match_obj[5]
	# # print(content)

	# match_obj = re.search(r"^(^|[^a-z]+)?whether (@CN@'s|his|her|its|their|our|your|my )?(@CN@|[a-z]+) did ([a-z]+)([^a-z]|$)(.*)$", content)
	# if match_obj is not None:
	# 	match_obj = match_obj.groups("")
	# 	content = match_obj[0] + "whether " + match_obj[1] + match_obj[2] + " " + past_verb(match_obj[3]) + match_obj[4] + match_obj[5]
	# # print(content)

	# content = re.sub("\?$", "", content)
	# print(content)

	return content

def check_wh(content):
	# check if the conveying clause is a wh-question or not
	# IN DEVELOPMENT: need a way to catch the whole subject

	# match_obj = re.search(r"^([^a-z]+)?(how|what|when|why|who|whom|whose|which) (shan't|do|does|did|is|are|was|were|will|shall|would|should|may|might|can|could|have|has|had)(n't)? (@CN@'s|his|her|its|their|our|your|my )?(@CN@|[a-z]+)([^a-z])(.*)$", content)
	# if match_obj is not None:
	# 	match_obj = match_obj.groups("")
	# 	content = match_obj[0] + match_obj[1] + " " + match_obj[4] + match_obj[5] + " " + match_obj[2] + match_obj[3] + match_obj[6] + match_obj[7]

	# match_obj = re.search(r"^([^a-z]+)?(how|what|when|why|who|whom|whose|which) (@CN@'s|his|her|its|their|our|your|my )?(@CN@|[a-z]+) do ([a-z]+)([^a-z])(.*)$", content)
	# if match_obj is not None:
	# 	match_obj = match_obj.groups("")
	# 	content = match_obj[0] + match_obj[1] + " " + match_obj[2] + match_obj[3] + " " + match_obj[4] + match_obj[5] + match_obj[6]

	# match_obj = re.search(r"^([^a-z]+)?(how|what|when|why|who|whom|whose|which) (@CN@'s|his|her|its|their|our|your|my )?(@CN@|[a-z]+) does ([a-z]+)([^a-z])(.*)$", content)
	# if match_obj is not None:
	# 	match_obj = match_obj.groups("")
	# 	content = match_obj[0] + match_obj[1] + " " + match_obj[2] + match_obj[3] + " " + singular_3rd_person(match_obj[4]) + match_obj[5] + match_obj[6]

	# match_obj = re.search(r"^([^a-z]+)?(how|what|when|why|who|whom|whose|which) (@CN@'s|his|her|its|their|our|your|my )?(@CN@|[a-z]+) did ([a-z]+)([^a-z])(.*)$", content)
	# if match_obj is not None:
	# 	match_obj = match_obj.groups("")
	# 	content = match_obj[0] + match_obj[1] + " " + match_obj[2] + match_obj[3] + " " + past_verb(match_obj[4]) + match_obj[5] + match_obj[6]

	return content


def pov_converted(content):
	# KNOWN ISSUE: overlapping cases of the word "her" (possessive or object?)
	# request further context handling

	# content = re.sub(r"(^|[^a-z])(@CN@'s|their|his|her|our)([^a-z]|$)", r"\1your\3", content)
	# content = re.sub(r"(^|[^a-z])(is )(@CN@|he|she|they|we)([^a-z]|$)", r"\1are \3\4", content)
	# content = re.sub(r"(^|[^a-z])(isn't )(@CN@|he|she|they|we)([^a-z]|$)", r"\1aren't \3\4", content)
	# content = re.sub(r"(^|[^a-z])(does )(@CN@|he|she|they|we)([^a-z]|$)", r"\1do \3\4", content)
	# content = re.sub(r"(^|[^a-z])(doesn't )(@CN@|he|she|they|we)([^a-z]|$)", r"\1don't \3\4", content)
	# content = re.sub(r"(^|[^a-z])(has )(@CN@|he|she|they|we)([^a-z]|$)", r"\1have \3\4", content)
	# content = re.sub(r"(^|[^a-z])(hasn't )(@CN@|he|she|they|we)([^a-z]|$)", r"\1haven't \3\4", content)
	# content = re.sub(r"(^|[^a-z])(@CN@|he|she|they|we) (doesn't)([^a-z]|$)", r"\1\2 don't\4", content)
	# content = re.sub(r"(^|[^a-z])(@CN@|he|she|they|we) (hasn't)([^a-z]|$)", r"\1\2 haven't\4", content)
	# content = re.sub(r"(^|[^a-z])(@CN@|he|she|they|we)('s)([^a-z]|$)", r"\1\2're\4", content)
	# content = re.sub(r"(^|[^a-z])(@CN@|he|she|they|we)( is)([^a-z]|$)", r"\1\2 are\4", content)
	# content = re.sub(r"(^|[^a-z])(@CN@|he|she|they|we)( isn't)([^a-z]|$)", r"\1\2 aren't\4", content)
	# content = re.sub(r"(^|[^a-z])(@CN@|he|she|they|we)([^a-z])(.+?[a-z]+?)(s)?([^a-z]|$)", r"\1you\3\4\6", content)
	# content = re.sub(r"(^|[^a-z])(@CN@|him|her|them|us)([^a-z]|$)", r"\1you\3", content)
	# content = re.sub(r"(^|[^a-z])(im)([^a-z]|$)", r"\1i'm\3", content)
	# content = re.sub(r"(^|[^a-z])(i'm)([^a-z]|$)", r"\1they're\3", content)
	# content = re.sub(r"(^|[^a-z])(i am)([^a-z]|$)", r"\1they are\3", content)
	# content = re.sub(r"(^|[^a-z])(i)([^a-z]|$)", r"\1they\3", content)
	# content = re.sub(r"(^|[^a-z])(my)([^a-z]|$)", r"\1their\3", content)
	# content = re.sub(r"(^|[^a-z])(me)([^a-z]|$)", r"\1them\3", content)

	# content = check_yesno(content)
	# content = check_wh(content)

	return content

greetings = [
	"hi @CN@ , @SCN@ ",
	"hello @CN@ , @SCN@ ",
	"hey @CN@ , @SCN@ ",
]

# rule_lists = [
# 	r"(ask) (my |our |the |that )?(friend )?@CN@ about[^a-z ]?(.+)[^a-z ]?", # ask about
# 	r"(ask|tell|call|notify|request|enquire) (my |our |the |that )?(friend )?@CN@ to[^a-z ]?(.+)[^a-z ]?", # request <activity>
# 	r"(ask) (my |our |the |that )?(friend )?@CN@ for[^a-z ]?(.+)[^a-z ]?", # request <thing>
# 	r"(tell|remind|inform|notify|update|text|say to|message|write) (my |our |the |that )?(friend )?@CN@ that[^a-z ]?(.+)[^a-z ]?", # inform
# 	r"(invite) (my |our |the |that )?(friend )?@CN@ (to|for)[^a-z ]?(.+)[^a-z ]?", # invitation
# 	r"(ask|tell|remind|invite|call|inform|notify|query|remember|send|advise|alert|check|mail|need|update|request|enquire|text|message|contact|write|give|warn|email) (my |our |the |that )?(friend )?@CN@[^a-z ]?(.+)[^a-z ]?", #verb
# 	r"(make sure|be sure) (my |our |the |that )?(friend )?@CN@[^a-z ]?(.+)[^a-z ]?", # assurance
# 	r"(to) (my |our |the |that )?(friend )?@CN@[^a-z ]?(.+)[^a-z ]?", # to
# 	r"(from|with) (my |our |the |that )?(friend )?@CN@[^a-z ]?(.+)[^a-z ]?", # query w/ from/with
# 	r"let (my |our |the |that )?(friend )?@CN@ know[^a-z ]?(.+)[^a-z ]?", # statement w/ let
# 	r"(if|whether) @CN@[^a-z ]?(.+)[^a-z ]?", # clear askyn
# 	r"(do|don't|did|didn't|does|doesn't|will|won't|should|shouldn't|shall|shan't|is|isn't|are|aren't|was|wasn't|were|weren't) (my |our |the |that )?(friend )?@CN@[^a-z ]?(.+)[^a-z ]?", # more askyn
# 	r"@CN@(.+)" # placeholder
# ]

def get_proper_response(sentence, re_index, match_obj):
	# if re_index == 0:
	# 	conveyed_content = match_obj.group(4)
	# 	if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

	# 	return greetings[np.random.randint(0, len(greetings))] + "wants to know about" + pov_converted(conveyed_content)

	# if re_index == 1:
	# 	conveyed_content = match_obj.group(4)
	# 	if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

	# 	return greetings[np.random.randint(0, len(greetings))] + "wants you to" + pov_converted(conveyed_content)

	# if re_index == 2:
	# 	conveyed_content = match_obj.group(4)
	# 	if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

	# 	return greetings[np.random.randint(0, len(greetings))] + "requests for" + pov_converted(conveyed_content)

	# if re_index == 3:
	# 	conveyed_content = match_obj.group(4)
	# 	if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

	# 	return greetings[np.random.randint(0, len(greetings))] + "says that" + pov_converted(conveyed_content)

	# if re_index == 4:
	# 	conveyed_content = match_obj.group(5)
	# 	if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

	# 	return greetings[np.random.randint(0, len(greetings))] + "invites you to" + pov_converted(conveyed_content)

	# if re_index == 5:
	# 	verb_used = match_obj.group(1)
	# 	conveyed_content = match_obj.group(4)
	# 	if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

	# 	return greetings[np.random.randint(0, len(greetings))] + singular_3rd_person(verb_used) + " you" + pov_converted(conveyed_content)

	# if re_index == 6:
	# 	certainty_form = match_obj.group(1)
	# 	conveyed_content = match_obj.group(4)
	# 	if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

	# 	return greetings[np.random.randint(0, len(greetings))] + "wants to " + certainty_form + " you" + pov_converted(conveyed_content)

	# if re_index == 7:
	# 	conveyed_content = match_obj.group(4)
	# 	if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

	# 	return greetings[np.random.randint(0, len(greetings))] + "says to you" + pov_converted(conveyed_content)

	# if re_index == 8:
	# 	conveyed_content = match_obj.group(4)
	# 	if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

	# 	return greetings[np.random.randint(0, len(greetings))] + "wants to ask from you" + pov_converted(conveyed_content)

	# if re_index == 9:
	# 	conveyed_content = match_obj.group(3)
	# 	if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

	# 	return greetings[np.random.randint(0, len(greetings))] + "wants to let you know" + pov_converted(conveyed_content)

	# if re_index == 10:
	# 	if_whether = match_obj.group(1)
	# 	conveyed_content = match_obj.group(2)
	# 	if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

	# 	return greetings[np.random.randint(0, len(greetings))] + "wants to know " + if_whether + " you" + pov_converted(conveyed_content)

	# if re_index == 11:
	# 	auxiliary = match_obj.group(1)
	# 	conveyed_content = match_obj.group(4)
	# 	if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

	# 	return greetings[np.random.randint(0, len(greetings))] + "wants to know if you " + de_negative(auxiliary) + " " + pov_converted(conveyed_content)

	# if re_index == 12:
	# 	conveyed_content = match_obj.group(1)
	# 	if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

	# 	return greetings[np.random.randint(0, len(greetings))] + "says that" + pov_converted(conveyed_content)

	return None

def process_response(pos_tags):
	pass

if __name__ == "__main__":
	for index in range(len(corpus.rows)):
		sentence = preprocess(str(corpus.get_row(index)["input"]))
		pos_tags = None

		pos_tags = pos_tagger(tokenizer(sentence))

		pos_tags = noun_chunker(pos_tags)

		response = process_response(pos_tags)
		
		print(response)