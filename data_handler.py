import re

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