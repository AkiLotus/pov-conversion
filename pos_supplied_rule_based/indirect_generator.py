import sys, re
sys.path.append("../")
from data_handler import Utilities
import sentence_rules

tagfile = open(sys.argv[1], "r")
begin_regex_pattern = r"(^VB/\d+ (?:TO/\d+ )?(?:NP/\d+ )?@CN@/\d+(?: ,/\d+)?)"


def split_contents(word_list, tag_list, tag_string):
	verb_begin, content_tags, content = None, None, None

	match_object = re.search(begin_regex_pattern, tag_string)

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


rules = [
	sentence_rules.transform_how_to,
	sentence_rules.transform_askwh_with_inversion,
	sentence_rules.transform_askwh_without_inversion,
	sentence_rules.transform_ask_for,
	sentence_rules.transform_ask_about,
	sentence_rules.transform_invite,
	sentence_rules.transform_request,
	sentence_rules.transform_let_know,
	sentence_rules.transform_indirect_askyn,
	sentence_rules.transform_direct_askyn,
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