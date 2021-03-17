from os.path import expanduser
from vncorenlp import VnCoreNLP
import re

home = expanduser("~")
vncorenlp_file = home + '/VnCoreNLP-1.1.1/VnCoreNLP-1.1.1.jar'

if __name__ == "__main__":
	with VnCoreNLP(vncorenlp_file) as vncorenlp:
		for line in open("input_train.txt", "r").readlines():
			if re.search(r"^.+?có thể.+?@", line) is not None and re.search(r"^.+?@.+?@.+?có thể", line) is None:
				line = re.sub(r" ((có )?được )?không(\?)?$", r"", line)

			tags = vncorenlp.pos_tag(line.strip())[0]
		
			true_tags = []
			index = 0
			while index < len(tags):
				if index + 2 < len(tags) and tags[index][0] == "@" and tags[index+1][0] == "CN" and tags[index+2][0] == "@":
					true_tags.append(("@CN@", "@CN@"))
					index += 3
				else:
					true_tags.append(tags[index])
					index += 1
	
			print(true_tags)