import sys, re, json
import numpy as np
np.random.seed(seed=170299)
sys.path.append("../")
import data_handler
from nltk.corpus import wordnet

corpus = data_handler.TSVCorpus(sys.argv[1])
irregular_verbs = json.loads(open("../resources/english-irregular-verbs.json", "r").read())


def pov_converted(content, source_sentence):
	# KNOWN ISSUE: overlapping cases of the word "her" (possessive or object?)
	# request further context handling

	content = re.sub(r"(^|[^a-z])(@CN@|anh ấy|cô ấy|họ|chúng tôi)([^a-z]|$)", r"\1bạn\3", content)
	content = re.sub(r"(^|[^a-z])(tôi)([^a-z]|$)", r"\1họ\3", content)

	if re.search(r"^.+?có thể.+?@", source_sentence) is not None and re.search(r"^.+?@.+?@.+?có thể", source_sentence) is None:
		content = re.sub(r" ((có )?được )?không(\?)?$", r"", content)

	# content = re.sub(r"\?$", r"", content)

	return content

greetings = [
	"chào @CN@ , @SCN@ ",
	"xin chào @CN@ , @SCN@ ",
	"này @CN@ , @SCN@ ",
]

rule_lists = [
	r"(hỏi) (bạn tôi )?@CN@,(.+)[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?", # ask
	r"(hỏi) (bạn tôi )?@CN@ về[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?(.+)[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?", # ask about
	r"(hỏi) (bạn tôi )?@CN@ (cho|để (biết thêm (thông tin)?)? về)[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?(.+)[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?", # request <thing>
	r"(nói|nói với|nhắc|nhắc nhở|thông báo|thông tin|thông báo cho|thông tin cho|cập nhật|cập nhật cho) (bạn tôi )?@CN@ rằng[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?(.+)[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?", # inform
	r"(mời) (bạn tôi )?@CN@ (đến|cho)[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?(.+)[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?", # invitation
	r"(hỏi) (bạn tôi )?@CN@[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?(.+)[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?", # ask
	r"(nhờ|yêu cầu|hỏi|bảo|bảo với|gọi) (bạn tôi )?@CN@( để| hỏi xem| để hỏi xem)?[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?(.+)[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?", # request <activity>
	r"(hỏi|nhờ|yêu cầu|nói với|bảo|bảo với|gọi|nói|nhắc|nhắc nhở|thông báo|thông tin|thông báo cho|thông tin cho|cập nhật|cập nhật cho|nhớ|gửi|cảnh báo|kiểm tra|mail|cần|nhắn tin cho|nhắn tin|liên lạc|viêt|viết cho|cho|email|xin) (bạn tôi )?@CN@[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?(.+)[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?", #verb
	r"(đảm bảo rằng|chắc chắn rằng|đảm bảo) (bạn tôi )?@CN@( rằng| nhớ rằng)[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?(.+)[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?", # assurance
	r"(cho) (bạn tôi )?@CN@ biết[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?(.+)[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?", # statement w/ let
	r"(xem|nếu) (bạn tôi )?@CN@[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?(.+)[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂẾưăạảấầẩẫậắằẳẵặẹẻẽềềểếỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ ]?", # clear askyn
	r"@CN@(.+)" # placeholder
]

def get_proper_response(sentence, re_index, match_obj):
	if re_index == 0:
		conveyed_content = match_obj.group(3)
		if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

		return greetings[np.random.randint(0, len(greetings))] + "muốn hỏi" + pov_converted(conveyed_content, sentence)

	if re_index == 1:
		conveyed_content = match_obj.group(3)
		if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

		return greetings[np.random.randint(0, len(greetings))] + "muốn biết về" + pov_converted(conveyed_content, sentence)

	if re_index == 2:
		conveyed_content = match_obj.group(6)
		if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

		return greetings[np.random.randint(0, len(greetings))] + "muốn" + pov_converted(conveyed_content, sentence)

	if re_index == 3:
		conveyed_content = match_obj.group(3)
		if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

		return greetings[np.random.randint(0, len(greetings))] + "nói rằng" + pov_converted(conveyed_content, sentence)

	if re_index == 4:
		conveyed_content = match_obj.group(4)
		if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

		return greetings[np.random.randint(0, len(greetings))] + "mời bạn tới" + pov_converted(conveyed_content, sentence)

	if re_index == 5:
		conveyed_content = match_obj.group(3)
		if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

		return greetings[np.random.randint(0, len(greetings))] + "muốn hỏi" + pov_converted(conveyed_content, sentence)

	if re_index == 6:
		conveyed_content = match_obj.group(4)
		if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

		return greetings[np.random.randint(0, len(greetings))] + "muốn bạn" + pov_converted(conveyed_content, sentence)

	if re_index == 7:
		verb_used = match_obj.group(1)
		conveyed_content = match_obj.group(3)
		if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

		return greetings[np.random.randint(0, len(greetings))] + verb_used + " bạn" + pov_converted(conveyed_content, sentence)

	if re_index == 8:
		certainty_form = match_obj.group(1)
		conveyed_content = match_obj.group(4)
		if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

		return greetings[np.random.randint(0, len(greetings))] + "muốn " + certainty_form + " bạn" + pov_converted(conveyed_content, sentence)

	if re_index == 9:
		conveyed_content = match_obj.group(3)
		if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

		return greetings[np.random.randint(0, len(greetings))] + "muốn cho bạn biết" + pov_converted(conveyed_content, sentence)

	if re_index == 10:
		if_whether = match_obj.group(1)
		conveyed_content = match_obj.group(3)
		if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

		return greetings[np.random.randint(0, len(greetings))] + "muốn biết " + if_whether + " bạn" + pov_converted(conveyed_content, sentence)

	if re_index == 11:
		conveyed_content = match_obj.group(1)
		if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

		return greetings[np.random.randint(0, len(greetings))] + "nói rằng" + pov_converted(conveyed_content, sentence)

	return None

if __name__ == "__main__":
	for index in range(len(corpus.rows)):
		sentence = str(corpus.get_row(index)["input"])

		response = None

		for re_index in range(len(rule_lists)):
			match_obj = re.search(rule_lists[re_index], sentence)

			if match_obj is not None:
				response = get_proper_response(sentence, re_index, match_obj)
				break
		else:
			sentence = re.sub(r"@SCN@", r"@CN@" ,sentence)

			for re_index in range(len(rule_lists)):
				match_obj = re.search(rule_lists[re_index], sentence)

				if match_obj is not None:
					response = get_proper_response(sentence, re_index, match_obj)
					break
			else:
				conveyed_content = sentence
				if len(conveyed_content) and conveyed_content[0] != " ": conveyed_content = " " + conveyed_content

				response = greetings[np.random.randint(0, len(greetings))] + "nói rằng" + pov_converted(conveyed_content, sentence)

		
		print(response)