import re
import generating_materials, point_of_view_modifier


def get_tag_string(tag_list):
	return " ".join(["{}/{}".format(tag_list[index], index) for index in range(len(tag_list))])


def default_response(content_tags, content):
	return generating_materials.random_greetings() + "nói rằng " + point_of_view_modifier.indirect_speech_convert(" ".join(content).replace("_", " "))


def transform_question(verb_begin, content_tags, content):
	if verb_begin != "hỏi": return None

	if len(content_tags) == 0 or content[0] != ",": return None

	actual_content = " ".join(content).replace("_", " ")

	if_whether = ""

	if re.search(r"(không|à)\??$", actual_content) is not None and re.search(r"^liệu", actual_content) is None:
		if_whether = "liệu "

	return generating_materials.random_greetings() + "muốn hỏi " + if_whether + point_of_view_modifier.indirect_speech_convert(actual_content)


def transform_askin(verb_begin, content_tags, content):
	if verb_begin != "hỏi": return None

	if len(content_tags) == 0 or content[0] != "về": return None

	actual_content = content

	return generating_materials.random_greetings() + "muốn biết " + point_of_view_modifier.indirect_speech_convert(" ".join(actual_content).replace("_", " "))


def transform_request_thing(verb_begin, content_tags, content):
	if verb_begin != "hỏi": return None

	actual_content = " ".join(content).replace("_", " ")

	if not re.match(r"^cho|để (biết thêm (thông tin)?)? về", actual_content): return None

	return generating_materials.random_greetings() + "muốn hỏi " + point_of_view_modifier.indirect_speech_convert(actual_content)


def transform_stmt(verb_begin, content_tags, content):
	if not re.match(r"nói|nói với|nhắc|nhắc nhở|thông báo|thông tin|thông báo cho|thông tin cho|cập nhật|cập nhật cho", verb_begin): return None

	if len(content_tags) == 0 or (content[0] != "rằng"): return None

	actual_content = content

	return generating_materials.random_greetings() + "nói " + point_of_view_modifier.indirect_speech_convert(" ".join(actual_content).replace("_", " "))


def transform_invite(verb_begin, content_tags, content):
	if verb_begin != "mời": return None

	if len(content_tags) == 0 or (content[0] != "đến" and content[0] != "cho"): return None

	actual_content = content

	return generating_materials.random_greetings() + "mời bạn tới " + point_of_view_modifier.indirect_speech_convert(" ".join(actual_content[1:]).replace("_", " "))


def transform_ask(verb_begin, content_tags, content):
	if verb_begin != "hỏi": return None

	actual_content = " ".join(content).replace("_", " ")

	if_whether = ""

	if re.search(r"(không|à)\??$", actual_content) is not None and re.search(r"^liệu", actual_content) is None:
		if_whether = "liệu "

	return generating_materials.random_greetings() + "muốn hỏi " + if_whether + point_of_view_modifier.indirect_speech_convert(actual_content)


def transform_reqact(verb_begin, content_tags, content):
	if not re.match(r"nhờ|yêu cầu|hỏi|bảo|bảo với|gọi", verb_begin): return None

	actual_content = content

	return generating_materials.random_greetings() + "muốn bạn " + point_of_view_modifier.indirect_speech_convert(" ".join(actual_content).replace("_", " "))


def transform_assurance(verb_begin, content_tags, content):
	if not re.match(r"đảm bảo|chắc chắn", verb_begin): return None

	if len(content_tags) == 0 or content[0] != "rằng": return None

	actual_content = content[1:]

	return generating_materials.random_greetings() + "muốn " + verb_begin + " bạn " + point_of_view_modifier.indirect_speech_convert(" ".join(actual_content).replace("_", " "))


def transform_let_know(verb_begin, content_tags, content):
	if not re.match(r"cho", verb_begin): return None

	if len(content_tags) == 0 or content[0] != "rằng": return None

	actual_content = content

	return generating_materials.random_greetings() + "muốn cho bạn biết " + point_of_view_modifier.indirect_speech_convert(" ".join(actual_content).replace("_", " "))


def transform_verb(verb_begin, content_tags, content):
	actual_content = content

	return generating_materials.random_greetings() + verb_begin + " bạn " + point_of_view_modifier.indirect_speech_convert(" ".join(actual_content).replace("_", " "))


def transform_general(verb_begin, content_tags, content):
	actual_content = content

	return generating_materials.random_greetings() + "muốn hỏi " + point_of_view_modifier.indirect_speech_convert(" ".join(actual_content).replace("_", " "))