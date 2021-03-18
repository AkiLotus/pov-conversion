from os.path import expanduser
from vncorenlp import VnCoreNLP
import re, sys

home = expanduser("~")
vncorenlp_file = home + '/VnCoreNLP-1.1.1/VnCoreNLP-1.1.1.jar'

if __name__ == "__main__":
	with VnCoreNLP(vncorenlp_file) as vncorenlp:
		for line in open(sys.argv[1], "r").readlines():
			if re.search(r"^.+?có thể.+?@", line) is not None and re.search(r"^.+?@.+?@.+?có thể", line) is None:
				line = re.sub(r" ((có )?được )?không(\?)?$", r"", line)

			sentences = vncorenlp.pos_tag(line.strip())
		
			true_tags = []
			for tags in sentences:
				index = 0
				while index < len(tags):
					if index + 2 < len(tags) and tags[index][0] == "@" and tags[index+2][0] == "@":
						word = "".join([e1 for e1, _ in tags[index:index+3]])
						true_tags.append((word, word))
						index += 3
					else:
						true_tags.append(tags[index])
						index += 1
	
			print(true_tags)