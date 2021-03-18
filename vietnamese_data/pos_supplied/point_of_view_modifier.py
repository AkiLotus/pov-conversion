import re


def indirect_speech_convert(content):
	content = re.sub(r"(^|[^a-z])(@CN@|anh ấy|cô ấy|họ|chúng tôi)([^a-z]|$)", r"\1bạn\3", content)
	content = re.sub(r"(^|[^a-z])(tôi)([^a-z]|$)", r"\1họ\3", content)

	# content = re.sub(r" là gì( \?)?$", r"\1", content)

	return content