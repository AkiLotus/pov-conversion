import json, re
import numpy as np
np.random.seed(170299)

irregular_verbs = json.loads(open("../resources/english-irregular-verbs.json", "r").read())

auxiliary_verbs = set([
	"do", "don't", "does", "doesn't", "did", "didn't", "will", "won't", "should", "shouldn't", "shall", "shan't", "can", "can't", "could", "couldn't", 
	"am", "is", "isn't", "are", "aren't", "was", "wasn't", "were", "weren't", "has", "hasn't", "have", "haven't", "had", "hadn't"
])


def is_irregular_verb(infinitive_verb):
	return (infinitive_verb in irregular_verbs)


def is_auxiliary_verb(verb):
	return (verb in auxiliary_verbs)


greets = [
	"hi @CN@ , @SCN@ ",
	"hello @CN@ , @SCN@ ",
	"hey @CN@ , @SCN@ ",
]


tobe_past_auxiliary = set(["was", "wasn't", "were", "weren't"])
tobe_pres_auxiliary = set(["am", "is", "isn't", "are", "aren't"])
todo_pres_auxiliary = set(["do", "don't", "does", "doesn't"])


def random_greetings():
	return greets[np.random.randint(0, len(greets))]


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