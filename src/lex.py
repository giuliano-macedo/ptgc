import json
import re
from grammar import grammar
from argparse import ArgumentParser
from itertools import chain,tee
import itertools
# https://stackoverflow.com/a/20415373/5133524
def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)   

separators={
	" ",
	",",
	";"
}
exclude={
	"\t",
	"\n"
}

parser=ArgumentParser()
parser.add_argument("input",help="source file")
args=parser.parse_args()

buff=""
out=[]
f=open("args.input)",encondig="utf-8")
for char,charnext in pairwise(chain.from_iterable(f)):
	if char in exclude:
		continue
	buff+=char
	if charnext not in separators:
		continue
	for i,(token_name,function) in enumerate(grammar.items()):
		token_valid,token_value=function(buff)
		if token_valid:
			print(f"{{{i}}}[{len(out)}]({repr(buff)}) match with {token_name}")
			out.append((token_name,token_value))
			buff=""
			break
f.close()
tokens={"tokens":out}
# print(json.dumps(tokens,indent=4))
assert buff=="",repr(buff)
with open("tokens.json","w") as f:
	json.dump(tokens,f,indent=4)
