from nltk import pos_tag, word_tokenize, download
import re
import generating_materials


def process_verbs(auxiliary, verb):
	if auxiliary == "do": return [verb]
	if auxiliary == "does": return [generating_materials.singular_3rd_person(verb)]
	if auxiliary == "did": return [generating_materials.past_verb(verb)]

	return [auxiliary, verb]


def indirect_speech_convert(content_tags, content):
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
		if generating_materials.is_auxiliary_verb(content[index]):
			new_aux = content[index]

			if content[index] in generating_materials.tobe_pres_auxiliary:
				if content[index][-3:] == "n't": # negative
					if last_PRP != "you" and last_PRP != "i":
						new_aux = "isn't"
					else: new_aux = "aren't"
				else: # positive
					if last_PRP != "you" and last_PRP != "i":
						new_aux = "is"
					else: new_aux = "are"
			elif content[index] in generating_materials.tobe_past_auxiliary:
				if content[index][-3:] == "n't": # negative
					if last_PRP != "you" and last_PRP != "i":
						new_aux = "wasn't"
					else: new_aux = "weren't"
				else: # positive
					if last_PRP != "you" and last_PRP != "i":
						new_aux = "was"
					else: new_aux = "were"
			elif content[index] in generating_materials.todo_pres_auxiliary:
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
						words.append(generating_materials.de_singular(immediate_aux))
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