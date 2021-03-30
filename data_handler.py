import re
import numpy as np

class Utilities:
	def print_row(row, spacing=32):
		for item in row:
			formatted_item = str(item)
			if len(str(item)) > spacing-2:
				formatted_item = str(item)[:spacing-5] + "..."
			print(formatted_item + ' ' * (spacing - len(formatted_item)), end='')
		print()
	
	def extract_tag_from_line(line):
		line = re.sub(r"^\[(.+)\]$", r"\1", line)

		taglist = []
		token = ""
		quotation_mark = None
		for char in line:
			if token == "" and char != "(": continue
			if char == "'" or char == '"':
				if quotation_mark is None: quotation_mark = char
				elif quotation_mark == char:
					quotation_mark = None
				else:
					token += char
				continue
			token += char
			if char == ")":
				if quotation_mark is None:
					token = re.sub(r"^\((.+)\)$", r"\1", token)
					word, tag = token.split(", ")
					token = ""

					taglist.append((word, tag))
				else:
					token += char

		return taglist

class Word:
	def __init__(self, word_string: str):
		self.word = word_string.strip()

	def __eq__(self, other):
		return self.word == other.word
	
	def __str__(self):
		return self.word

class Sentence:
	def __init__(self, line: str):
		self.__words = []
		for token in line.strip().split():
			if token == '': continue
			self.__words.append(Word(token))
		
	def get_all_n_grams(self, n):
		n_grams = []

		for index in range(len(self.__words) - n + 1):
			n_grams.append(self.__words[index:index+n])
		
		return n_grams
	
	def get_tokens(self):
		return self.__words
	
	def get_word_by_index(self, index):
		return self.__words[index]
	
	def find_index(self, word):
		try:
			return self.__words.index(Word(word))
		except ValueError:
			return -1
	
	def __str__(self):
		return ' '.join(map(str, self.__words))

class TSVCorpus:
	def __init__(self, file_path, has_headers = True):
		file = open(file_path, "r")

		self.headers = []
		self.rows = []

		if has_headers:
			self.headers = file.readline().strip().split('\t')
		
		while True:
			try:
				row = file.readline().strip().split('\t')
				if len("".join(row)) == 0: break

				if len(self.headers) == 0:
					self.headers = [x for x in range(len(row))]
				
				dicted_row = {}
				for index in range(len(row)):
					dicted_row[self.headers[index]] = Sentence(row[index])
				
				self.rows.append(dicted_row)
			except EOFError: break
	
	def get_row(self, index, as_list=False):
		if not as_list: return self.rows[index]

		list_output = []
		for key in self.headers: list_output.append(self.rows[index][key])
		return list_output

	def __str__(self):
		Utilities.print_row([""] + self.headers)
		for index in range(len(self.rows)):
			itemlist = [index]
			for key in self.headers: itemlist.append(self.rows[index][key])
			Utilities.print_row(itemlist)
		return ''

class TSVFile:
	def __init__(self, file_path = "", has_headers = True):

		self.headers = []
		self.rows = []

		if file_path:
			file = open(file_path, "r")

			if has_headers:
				self.headers = file.readline().strip().split('\t')
			
			while True:
				try:
					row = file.readline().strip().split('\t')
					if len("".join(row)) == 0: break

					if len(self.headers) == 0:
						self.headers = [x for x in range(len(row))]
					
					dicted_row = {}
					for index in range(len(row)):
						dicted_row[self.headers[index]] = row[index]
					
					self.rows.append(dicted_row)
				except EOFError: break
	
	def get_row(self, index, as_list=False):
		if not as_list: return self.rows[index]

		list_output = []
		for key in self.headers: list_output.append(self.rows[index][key])
		return list_output
	
	def get_column(self, string, as_list=False):
		list_output = []

		for index in range(len(self.rows)):
			list_output.append(self.rows[index][string])

		return list_output
	
	def random_split(self, p1_proportion = 0.5, seed = 170299):
		length = len(self.rows)
		np.random.seed(seed)
		permutation = np.random.permutation(length) + 1

		split_1, split_2 = TSVFile(), TSVFile()
		split_1.headers = [x for x in self.headers]
		split_2.headers = [x for x in self.headers]
		for index in range(length):
			if permutation[index] <= p1_proportion * length:
				split_1.rows.append(self.rows[index])
			else:
				split_2.rows.append(self.rows[index])
		return split_1, split_2

	def __str__(self):
		Utilities.print_row([""] + self.headers)
		for index in range(len(self.rows)):
			itemlist = [index]
			for key in self.headers: itemlist.append(self.rows[index][key])
			Utilities.print_row(itemlist)
		return ''