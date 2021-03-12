import re
import generating_materials, point_of_view_modifier


def get_tag_string(tag_list):
	return " ".join(["{}/{}".format(tag_list[index], index) for index in range(len(tag_list))])


def default_response(content_tags, content):
	return generating_materials.random_greetings() + "says that " + point_of_view_modifier.indirect_speech_convert(content_tags, content)


def transform_how_to(verb_begin, content_tags, content):
	if verb_begin != "ask": return None

	actual_content, actual_content_tags = None, None

	if content[0] == "how" and content[1] == "to":
		actual_content = content[2:]
		actual_content_tags = content_tags[2:]

		return generating_materials.random_greetings() + "wants to know how to " + point_of_view_modifier.indirect_speech_convert(actual_content_tags, actual_content)
	elif content[0] == "how to":
		actual_content = content[1:]
		actual_content_tags = content_tags[1:]

		return generating_materials.random_greetings() + "wants to know how to " + point_of_view_modifier.indirect_speech_convert(actual_content_tags, actual_content)
	else:
		return None


def transform_askwh_with_inversion(verb_begin, content_tags, content):
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
	
	return generating_materials.random_greetings() + "asks " + point_of_view_modifier.indirect_speech_convert(actual_content_tags, actual_content)


def transform_askwh_without_inversion(verb_begin, content_tags, content):
	if verb_begin != "ask": return None

	content_tag_string = get_tag_string(content_tags)

	wh_question_regex = r"(^W[A-Z]*?/\d+ (?:NP/\d+ )?(?:PRP|NP|RB|FW)/\d+ V[A-Z]*?/\d+)"

	match_object = re.search(wh_question_regex, content_tag_string)

	if match_object is None: return None

	compound = match_object.group(1)
	tag_sublist = compound.split()
	start_index = int(tag_sublist[0].split("/")[1])

	actual_content = content[start_index:]
	actual_content_tags = content_tags[start_index:]
	
	return generating_materials.random_greetings() + "asks " + point_of_view_modifier.indirect_speech_convert(actual_content_tags, actual_content)


def transform_ask_for(verb_begin, content_tags, content):
	if verb_begin != "ask": return None

	actual_content, actual_content_tags = None, None

	if content[0] == "for":
		actual_content = content[1:]
		actual_content_tags = content_tags[1:]

		return generating_materials.random_greetings() + "requests you for " + point_of_view_modifier.indirect_speech_convert(actual_content_tags, actual_content)
	else:
		return None


def transform_ask_about(verb_begin, content_tags, content):
	if verb_begin != "ask": return None

	actual_content, actual_content_tags = None, None

	if content[0] == "about":
		actual_content = content[1:]
		actual_content_tags = content_tags[1:]

		return generating_materials.random_greetings() + "wants to know about " + point_of_view_modifier.indirect_speech_convert(actual_content_tags, actual_content)
	else:
		return None


def transform_invite(verb_begin, content_tags, content):
	if verb_begin != "invite": return None

	actual_content, actual_content_tags = None, None

	if content[0] == "to" or content[0] == "for":
		actual_content = content[1:]
		actual_content_tags = content_tags[1:]

		return generating_materials.random_greetings() + "invites you to " + point_of_view_modifier.indirect_speech_convert(actual_content_tags, actual_content)
	else:
		return None


def transform_request(verb_begin, content_tags, content):
	actual_content, actual_content_tags = None, None

	if content[0] == "to":
		actual_content = content[1:]
		actual_content_tags = content_tags[1:]

		return generating_materials.random_greetings() + generating_materials.singular_3rd_person(verb_begin) + " you to " + point_of_view_modifier.indirect_speech_convert(actual_content_tags, actual_content)
	else:
		return None


def transform_let_know(verb_begin, content_tags, content):
	if verb_begin != "let": return None

	actual_content, actual_content_tags = None, None

	if content[0] == "know":
		actual_content = content[1:]
		actual_content_tags = content_tags[1:]

		return generating_materials.random_greetings() + "wants to let you know " + point_of_view_modifier.indirect_speech_convert(actual_content_tags, actual_content)
	else:
		return None


def transform_indirect_askyn(verb_begin, content_tags, content):
	actual_content, actual_content_tags = None, None

	if content[0] == "if" or content[0] == "whether":
		actual_content = content[1:]
		actual_content_tags = content_tags[1:]

		return generating_materials.random_greetings() + "wants to know " + content[0] + " " + point_of_view_modifier.indirect_speech_convert(actual_content_tags, actual_content)
	else:
		return None


def transform_direct_askyn(verb_begin, content_tags, content):
	actual_content, actual_content_tags = None, None

	if generating_materials.is_auxiliary_verb(content[0]) and (content_tags[1] == "PRP" or content_tags[1] == "NP" or content_tags[1] == "RB" or content_tags[1] == "FW"):
		actual_content = content[1:2] + content[0:1] + content[2:]
		actual_content_tags = content_tags[1:2] + content_tags[0:1] + content_tags[2:]

		return generating_materials.random_greetings() + "wants to know whether " + point_of_view_modifier.indirect_speech_convert(actual_content_tags, actual_content)
	else:
		return None


def transform_general(verb_begin, content_tags, content):
	content_tag_string = get_tag_string(content_tags)

	wh_question_regex = r"(^(?:IN/\d+ )?[^VWIT][A-Z]*?/\d+)"

	match_object = re.search(wh_question_regex, content_tag_string)

	if match_object is None: return None

	compound = match_object.group(1)
	tag_sublist = compound.split()
	start_index = int(tag_sublist[0].split("/")[1])

	if len(tag_sublist) == 2 and content[start_index] != "that": return None

	actual_content = content[start_index:]
	actual_content_tags = content_tags[start_index:]
	
	return generating_materials.random_greetings() + generating_materials.singular_3rd_person(verb_begin) + " you " + point_of_view_modifier.indirect_speech_convert(actual_content_tags, actual_content)