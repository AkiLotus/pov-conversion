import sys, re
sys.path.append("../../")
from data_handler import Utilities
import sentence_rules

tagfile = open(sys.argv[1], "r")


def split_contents(word_list, tag_list, tag_string):
	verb_begin, content_tags, content = None, None, None

	verb_begin = None
	content_tags = tag_list
	content = word_list

	passed_CN = None

	for index in range(len(tag_list)):
		if tag_list[index] == "@CN@" and passed_CN is None:
			passed_CN = index
			content_tags = tag_list[index+1:]
			content = word_list[index+1:]
		elif passed_CN is None and tag_list[index] == "V":
			verb_begin = word_list[index].replace("_", " ")
		# elif passed_CN and re.match(r"[CENP]", tag_list[index][0]):
		# 	content_tags = tag_list[index:]
		# 	content = word_list[index:]
		# 	break
		elif passed_CN is not None and passed_CN == index - 1 and word_list[index] == ",":
			content_tags = tag_list[index+1:]
			content = word_list[index+1:]
			break
		elif passed_CN is not None and passed_CN < index - 1:
			break

	if passed_CN is None:
		verb_begin = None

	return verb_begin, content_tags, content


rules = [
	sentence_rules.transform_question,
	sentence_rules.transform_askin,
	sentence_rules.transform_request_thing,
	sentence_rules.transform_ask,
	sentence_rules.transform_stmt,
	sentence_rules.transform_invite,
	sentence_rules.transform_reqact,
	sentence_rules.transform_assurance,
	sentence_rules.transform_let_know,
	sentence_rules.transform_verb,
	sentence_rules.transform_general,
]


if __name__ == "__main__":
	while True:
		line = tagfile.readline().strip()
		if len(line) == 0: break

		tuple_list = Utilities.extract_tag_from_line(line)
		
		word_list = [word for word, _ in tuple_list]
		tag_list = [tag for _, tag in tuple_list]

		for index in range(len(tag_list)):
			if word_list[index][0] == "@":
				tag_list[index] = word_list[index]

		tag_string = sentence_rules.get_tag_string(tag_list)

		response = None

		verb_begin, content_tags, content = split_contents(word_list, tag_list, tag_string)

		if verb_begin is None:
			word_list = [word if word != "@SCN@" else "@CN@" for word in word_list]
			tag_list = [tag if tag != "@SCN@" else "@CN@" for tag in tag_list]

			tag_string = " ".join(["{}/{}".format(tag_list[index], index) for index in range(len(tag_list))])

			verb_begin, content_tags, content = split_contents(word_list, tag_list, tag_string)

		if verb_begin is None:
			response = sentence_rules.default_response(content_tags, content)
		else:
			for transformation_rule in rules:
				value = transformation_rule(verb_begin, content_tags, content)
				if value is not None:
					# print(transformation_rule)
					response = value
					break
			else:
				response = sentence_rules.default_response(content_tags, content)

		print(response)