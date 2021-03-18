import numpy as np
np.random.seed(170299)

greets = [
	"chào @CN@ , @SCN@ ",
	"xin chào @CN@ , @SCN@ ",
	"này @CN@ , @SCN@ ",
]

def random_greetings():
	return greets[np.random.randint(0, len(greets))]