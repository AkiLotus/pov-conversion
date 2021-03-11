# How to use the POS-supplied rule-based model:

1. Run `python3 stanford_pos_tagger.py > raw_pos_tagged.txt` for the primitive POS-tagged input file saved at `raw_pos_tagged.txt` (replace that with any name you wish).
2. Run `python3 word-chunker.py raw_pos_tagged.txt > chunked.txt` for chunking the `raw_pos_tagged.txt` file (or whatever name you chose from step 1) to get the better segmented input file saved at `chunked.txt` (replace that with any name you wish). This file will be used for the rule-based process.
3. Run `python3 indirect-generator chunked.txt > hypotheses.txt` to use the `chunked.txt` file (or whatever name you chose from step 2) to go through the rule-processing procedure and generate the hypotheses output at `hypotheses.txt`