import sys
sys.path.append("../")
from data_handler import TSVCorpus

def translate_text(target, text):
	"""Translates text into the target language.

	Target must be an ISO 639-1 language code.
	See https://g.co/cloud/translate/v2/translate-reference#supported_languages
	"""
	import six
	from google.cloud import translate_v2 as translate

	translate_client = translate.Client.from_service_account_json("akilotus_test.json")
	# translate_client = translate.Client.from_service_account_json("nlp-01-302507-64eaeb04e837.json")

	if isinstance(text, six.binary_type):
		text = text.decode("utf-8")

	# Text can also be a sequence of strings, in which case this method
	# will return a sequence of results for each text.
	result = translate_client.translate(text, target_language=target)

	return result["translatedText"]

if __name__ == "__main__":
	tsv = TSVCorpus(sys.argv[1])
	print("input\toutput\tlabel")
	for index in range(len(tsv.rows)):
		input_sentence = tsv.get_row(index)["input"]
		input_translated = translate_text("vi", str(input_sentence))
		output_sentence = tsv.get_row(index)["output"]
		output_translated = translate_text("vi", str(output_sentence))
		label = tsv.get_row(index)["label"]

		print(input_translated, output_translated, label, sep="\t")