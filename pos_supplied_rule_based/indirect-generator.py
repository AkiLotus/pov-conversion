import sys, re, json
import numpy as np
np.random.seed(seed=170299)
sys.path.append("../")
from data_handler import Utilities
from nltk import pos_tag, word_tokenize, download

tagfile = open(sys.argv[1], "r")
irregular_verbs = json.loads(open("../resources/english-irregular-verbs.json", "r").read())

greet_samples = [
	"hi @CN@ , @SCN@ ",
	"hello @CN@ , @SCN@ ",
	"hey @CN@ , @SCN@ ",
]

auxiliary_verbs = set([
	"do", "don't", "does", "doesn't", "did", "didn't", "will", "won't", "should", "shouldn't", "shall", "shan't", "can", "can't", "could", "couldn't", 
	"am", "is", "isn't", "are", "aren't", "was", "wasn't", "were", "weren't", "has", "hasn't", "have", "haven't", "had", "hadn't"
])

tobe_past_auxiliary = set(["was", "wasn't", "were", "weren't"])

tobe_pres_auxiliary = set(["am", "is", "isn't", "are", "aren't"])

todo_pres_auxiliary = set(["do", "don't", "does", "doesn't"])

extract_begin = r"(^VB/\d+ (?:TO/\d+ )?(?:NP/\d+ )?@CN@/\d+(?: ,/\d+)?)"

def get_tag_string(tag_list):
	return " ".join(["{}/{}".format(tag_list[index], index) for index in range(len(tag_list))])

def split_contents(word_list, tag_list, tag_string):
	verb_begin, content_tags, content = None, None, None

	match_object = re.search(extract_begin, tag_string)

	if match_object is None:
		content = word_list
		content_tags = tag_list
	else:
		compound = match_object.group(1)
		tag_sublist = compound.split()
		start_index = int(tag_sublist[0].split("/")[1])
		end_index = int(tag_sublist[-1].split("/")[1])

		verb_begin = word_list[start_index]

		content_tags = tag_list[end_index+1:]

		content = word_list[end_index+1:]

		if content[0] == "how" and content[1] == "come":
			content[0] = "why"
			content_tags[0] = "WRB"
			content.pop(1)
			content_tags.pop(1)

		if content[0] == "how come":
			content[0] = "why"
			content_tags[0] = "WRB"

	return verb_begin, content_tags, content

def greetings():
	return greet_samples[np.random.randint(0, len(greet_samples))]

def de_singular(aux):
	if aux[:2] == "is": return "are" + aux[2:]
	if aux[:3] == "was": return "were" + aux[3:]
	if aux[:3] == "has": return "have" + aux[3:]
	if aux[:4] == "does": return "do" + aux[4:]
	return aux

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

def process_verbs(auxiliary, verb):
	if auxiliary == "do": return [verb]
	if auxiliary == "does": return [singular_3rd_person(verb)]
	if auxiliary == "did": return [past_verb(verb)]

	return [auxiliary, verb]

def pov_converted(content_tags, content):
	if content is None: return ""

	for index in range(len(content)):
		if content[index] == "@CN@":
			content[index] = "you"
			if content_tags is not None: content_tags[index] = "PRP"
		if content[index] == "@SCN@":
			content[index] = "me"
			if content_tags is not None: content_tags[index] = "PRP"

	assert(len(content_tags) == len(content))

	words = []

	last_PRP = "you"
	immediate_aux = None

	for index in range(len(content)):
		if content[index] in auxiliary_verbs:
			new_aux = content[index]

			if content[index] in tobe_pres_auxiliary:
				if content[index][-3:] == "n't": # negative
					if last_PRP != "you" and last_PRP != "i":
						new_aux = "isn't"
					else: new_aux = "aren't"
				else: # positive
					if last_PRP != "you" and last_PRP != "i":
						new_aux = "is"
					else: new_aux = "are"
			elif content[index] in tobe_past_auxiliary:
				if content[index][-3:] == "n't": # negative
					if last_PRP != "you" and last_PRP != "i":
						new_aux = "wasn't"
					else: new_aux = "weren't"
				else: # positive
					if last_PRP != "you" and last_PRP != "i":
						new_aux = "was"
					else: new_aux = "were"
			elif content[index] in todo_pres_auxiliary:
				if content[index][-3:] == "n't": # negative
					if last_PRP != "you" and last_PRP != "i":
						new_aux = "doesn't"
					else: new_aux = "don't"
				else: # positive
					if last_PRP != "you" and last_PRP != "i":
						new_aux = "does"
					else: new_aux = "do"
			
			immediate_aux = new_aux
		else:
			if content_tags[index][0] == 'V' and immediate_aux is not None: # verb
				words += process_verbs(immediate_aux, content[index])
				immediate_aux = None
			else:
				if immediate_aux is not None:
					if len(words) > 0 and re.match(r"i|they|we|you", words[-1]):
						words.append(de_singular(immediate_aux))
					else:
						words.append(immediate_aux)
					immediate_aux = None

				if content_tags[index] == "PRP" or content_tags[index] == "FW":
					if content[index].lower() == "i":
						words.append("they")
						last_PRP = "i"
					elif content[index].lower() == "me":
						words.append("them")
						last_PRP = "i"
					elif re.match(r"he|she|they|we|you", content[index].lower()):
						words.append("you")
						last_PRP = "you"
					elif re.match(r"him|her|them|us|you", content[index].lower()):
						words.append("you")
						last_PRP = "you"
					else:
						last_PRP = "N/A"
				elif content_tags[index] == "PRP$":
					if content[index].lower() == "my":
						words.append("their")
						last_PRP = "i"
					elif re.match(r"his|her|their|our|your", content[index].lower()):
						words.append("your")
						last_PRP = "you"
					else:
						last_PRP = "N/A"
				elif content_tags[index] == "NP" and len(content[index].split()) > 1: # compound noun
					quick_tags = None
					try:
						quick_tags = pos_tag(word_tokenize(content[index]))
					except LookupError:
						download("averaged_perceptron_tagger")
						quick_tags = pos_tag(word_tokenize(content[index]))
					if quick_tags is not None:
						for quick_index in range(len(quick_tags)):
							if quick_tags[quick_index][1] != "PRP$": continue
							if quick_tags[quick_index][0].lower() == "my":
								quick_tags[quick_index] = ("their", quick_tags[quick_index][1])
							elif re.match(r"his|her|their|our|your", quick_tags[quick_index][0].lower()):
								quick_tags[quick_index] = ("your", quick_tags[quick_index][1])
					
					last_PRP = "N/A"
					
					new_word_list = []

					for word, tag in quick_tags:
						if tag == "POS" and len(new_word_list) > 0:
							new_word_list.append(new_word_list.pop() + word)
						else:
							new_word_list.append(word)
					
					words.append(" ".join(new_word_list))

				elif content_tags[index][0] == "V" and len(words) > 0 and re.match(r"i|they|we|you", words[-1]):
					words.append(re.sub(r"s$", r"", content[index]))
				elif content_tags[index] == "POS":
					words.append(words.pop() + content[index])
				else:
					if content[index] == "this":
						words.append("that")
					if content[index] == "these":
						words.append("those")
					else:
						words.append(content[index])

	# if words[-1] == '?': words.pop()

	return " ".join(words)

def default_response(content_tags, content):
	return greetings() + "says that " + pov_converted(content_tags, content)

def transform_1(verb_begin, content_tags, content):
	if verb_begin != "ask": return None

	actual_content, actual_content_tags = None, None

	if content[0] == "how" and content[1] == "to":
		actual_content = content[2:]
		actual_content_tags = content_tags[2:]

		return greetings() + "wants to know how to " + pov_converted(actual_content_tags, actual_content)
	elif content[0] == "how to":
		actual_content = content[1:]
		actual_content_tags = content_tags[1:]

		return greetings() + "wants to know how to " + pov_converted(actual_content_tags, actual_content)
	else:
		return None

def transform_2(verb_begin, content_tags, content):
	if verb_begin != "ask": return None

	content_tag_string = get_tag_string(content_tags)

	wh_question_regex = r"(^W[A-Z]*?/\d+ (?:NP/\d+ )?V[A-Z]*?/\d+ (?:PRP|NP|RB|FW)/\d+ V[A-Z]*?/\d+)"

	match_object = re.search(wh_question_regex, content_tag_string)

	if match_object is None: return None

	compound = match_object.group(1)
	tag_sublist = compound.split()
	start_index = int(tag_sublist[0].split("/")[1])
	end_index = int(tag_sublist[-1].split("/")[1])

	actual_content, actual_content_tags = [], []
	actual_content.append(content[start_index])
	actual_content_tags.append(content_tags[start_index])
	if len(tag_sublist) == 4: # no NP
		actual_content.append(content[start_index + 2])
		actual_content_tags.append(content_tags[start_index + 2])
		actual_content.append(content[start_index + 1])
		actual_content_tags.append(content_tags[start_index + 1])
		actual_content.append(content[start_index + 3])
		actual_content_tags.append(content_tags[start_index + 3])
	else:
		actual_content.append(content[start_index + 1])
		actual_content_tags.append(content_tags[start_index + 1])
		actual_content.append(content[start_index + 3])
		actual_content_tags.append(content_tags[start_index + 3])
		actual_content.append(content[start_index + 2])
		actual_content_tags.append(content_tags[start_index + 2])
		actual_content.append(content[start_index + 4])
		actual_content_tags.append(content_tags[start_index + 4])

	actual_content += content[end_index+1:]
	actual_content_tags += content_tags[end_index+1:]
	
	return greetings() + "asks " + pov_converted(actual_content_tags, actual_content)

def transform_2b(verb_begin, content_tags, content):
	if verb_begin != "ask": return None

	content_tag_string = get_tag_string(content_tags)

	wh_question_regex = r"(^W[A-Z]*?/\d+ (?:NP/\d+ )?(?:PRP|NP|RB|FW)/\d+ V[A-Z]*?/\d+)"

	match_object = re.search(wh_question_regex, content_tag_string)

	if match_object is None: return None

	compound = match_object.group(1)
	tag_sublist = compound.split()
	start_index = int(tag_sublist[0].split("/")[1])
	end_index = int(tag_sublist[-1].split("/")[1])

	actual_content = content[start_index:]
	actual_content_tags = content_tags[start_index:]
	
	return greetings() + "asks " + pov_converted(actual_content_tags, actual_content)

def transform_3(verb_begin, content_tags, content):
	if verb_begin != "ask": return None

	actual_content, actual_content_tags = None, None

	if content[0] == "for":
		actual_content = content[1:]
		actual_content_tags = content_tags[1:]

		return greetings() + "requests you for " + pov_converted(actual_content_tags, actual_content)
	else:
		return None

def transform_4(verb_begin, content_tags, content):
	if verb_begin != "ask": return None

	actual_content, actual_content_tags = None, None

	if content[0] == "about":
		actual_content = content[1:]
		actual_content_tags = content_tags[1:]

		return greetings() + "wants to know about " + pov_converted(actual_content_tags, actual_content)
	else:
		return None

def transform_5(verb_begin, content_tags, content):
	if verb_begin != "invite": return None

	actual_content, actual_content_tags = None, None

	if content[0] == "to" or content[0] == "for":
		actual_content = content[1:]
		actual_content_tags = content_tags[1:]

		return greetings() + "invites you to " + pov_converted(actual_content_tags, actual_content)
	else:
		return None

def transform_6(verb_begin, content_tags, content):
	actual_content, actual_content_tags = None, None

	if content[0] == "to":
		actual_content = content[1:]
		actual_content_tags = content_tags[1:]

		return greetings() + verb_begin + "s you to " + pov_converted(actual_content_tags, actual_content)
	else:
		return None

def transform_7(verb_begin, content_tags, content):
	if verb_begin != "let": return None

	actual_content, actual_content_tags = None, None

	if content[0] == "know":
		actual_content = content[1:]
		actual_content_tags = content_tags[1:]

		return greetings() + "wants to let you know " + pov_converted(actual_content_tags, actual_content)
	else:
		return None

def transform_8(verb_begin, content_tags, content):
	actual_content, actual_content_tags = None, None

	if content[0] == "if" or content[0] == "whether":
		actual_content = content[1:]
		actual_content_tags = content_tags[1:]

		return greetings() + "wants to know " + content[0] + " " + pov_converted(actual_content_tags, actual_content)
	else:
		return None

def transform_9(verb_begin, content_tags, content):
	actual_content, actual_content_tags = None, None

	if content[0] in auxiliary_verbs and (content_tags[1] == "PRP" or content_tags[1] == "NP" or content_tags[1] == "RB" or content_tags[1] == "FW"):
		actual_content = content[1:2] + content[0:1] + content[2:]
		actual_content_tags = content_tags[1:2] + content_tags[0:1] + content_tags[2:]

		return greetings() + "wants to know whether " + pov_converted(actual_content_tags, actual_content)
	else:
		return None

def transform_10(verb_begin, content_tags, content):
	content_tag_string = get_tag_string(content_tags)

	wh_question_regex = r"(^(?:IN/\d+ )?[^VWIT][A-Z]*?/\d+)"

	match_object = re.search(wh_question_regex, content_tag_string)

	if match_object is None: return None

	compound = match_object.group(1)
	tag_sublist = compound.split()
	start_index = int(tag_sublist[0].split("/")[1])
	end_index = int(tag_sublist[-1].split("/")[1])

	if len(tag_sublist) == 2 and content[start_index] != "that": return None

	actual_content = content[start_index:]
	actual_content_tags = content_tags[start_index:]

	# print(actual_content)
	
	return greetings() + singular_3rd_person(verb_begin) + " you " + pov_converted(actual_content_tags, actual_content)

rules = [
	transform_1,
	transform_2,
	transform_2b,
	transform_3,
	transform_4,
	transform_5,
	transform_6,
	transform_7,
	transform_8,
	transform_9,
	transform_10,
]

while True:
	line = tagfile.readline().strip()
	if len(line) == 0: break

	tuple_list = Utilities.extract_tag_from_line(line)
	
	word_list = [word for word, _ in tuple_list]
	tag_list = [tag for _, tag in tuple_list]

	for index in range(len(tag_list)):
		if word_list[index][0] == "@":
			tag_list[index] = word_list[index]

	tag_string = get_tag_string(tag_list)

	response = None

	verb_begin, content_tags, content = split_contents(word_list, tag_list, tag_string)

	if verb_begin is None:
		word_list = [word if word != "@SCN@" else "@CN@" for word in word_list]
		tag_list = [tag if tag != "@SCN@" else "@CN@" for tag in tag_list]

		tag_string = " ".join(["{}/{}".format(tag_list[index], index) for index in range(len(tag_list))])

		verb_begin, content_tags, content = split_contents(word_list, tag_list, tag_string)

	if verb_begin is None:
		response = default_response(content_tags, content)
	else:
		for transformation_rule in rules:
			value = transformation_rule(verb_begin, content_tags, content)
			if value is not None:
				# print(transformation_rule)
				response = value
				break
		else:
			response = default_response(content_tags, content)

	print(response)