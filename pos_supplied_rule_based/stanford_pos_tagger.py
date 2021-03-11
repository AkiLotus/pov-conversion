from nltk import word_tokenize, download
from nltk.tag.stanford import StanfordPOSTagger
from os.path import expanduser
import sys, re
sys.path.append("../")
import data_handler

corpus = data_handler.TSVCorpus("../data/test.tsv")
home = expanduser("~")
_path_to_model = home + '/stanford-postagger/models/english-bidirectional-distsim.tagger'
_path_to_jar = home + '/stanford-postagger/stanford-postagger.jar'
st = StanfordPOSTagger(model_filename=_path_to_model, path_to_jar=_path_to_jar)

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

def batch_pos_tagger(tokenized_sentences):
	raw_tagged_sentences = st.tag_sents(tokenized_sentences)

	tagged_sentences = []

	for raw_tags in raw_tagged_sentences:
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

		if nearest_VB_before_CN == -1 or first_CN == -1: # solely remove "can you"
			tagged_sentences.append(tags[2:])
		else: # remove everything before first @CN@
			tagged_sentences.append(tags[nearest_VB_before_CN:])

	return tagged_sentences

if __name__ == "__main__":
	preprocessed_sentences = []

	for index in range(len(corpus.rows)):
		sentence = str(corpus.get_row(index)["input"]).replace("’", "'")

		# preprocess
		sentence = re.sub(r"^([^(@CN@)]*) ?,? ?(please|kindly|gently|honou?red|honou?rly) ?,? ?", r"\1", sentence)
		sentence = re.sub(r"^(hi|hello|hey) ?,? ?", r"", sentence)
		sentence = re.sub(r"^([^(@CN@)]*) ?,? ?(can|could|may|might|will|would) you ?,? ?", r"\1", sentence)
		sentence = re.sub(r"^[a-hj-z][^a-z]", r"", sentence)
		sentence = re.sub(r"\"([a-z.\?!].+[a-z.\?!])\"", r"\1", sentence)
		sentence = re.sub(r"^i (want|need|order|command) (you )?to ?,? ?", r"", sentence)
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

		tokenized_sentence = tokenizer(sentence)

		preprocessed_sentences.append(tokenized_sentence)

		# pos_tags = pos_tagger(tokenizer(sentence))
		# print(pos_tags)
	
	tagged_sentences = batch_pos_tagger(preprocessed_sentences)
	for tagged_sentence in tagged_sentences: print(tagged_sentence)