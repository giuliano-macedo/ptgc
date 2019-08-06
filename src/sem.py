import json
from argparse import ArgumentParser
from collections import namedtuple

def extract_str(token):
	assert token.name=="STRING"
	return token.value[1:-1]
def split_tokens(tokens,*patterns_name):
	patterns=set(patterns_name)
	buff=[]
	for tok in tokens:
		if tok.name in patterns:
			if buff!=[]:
				yield buff
			buff=[]
		else:
			buff.append(tok)
	if buff!=[]:
		yield buff
def command_type(tokens):
	if tokens[0].name=="ID":
		if tokens[1].name=="ATTR":
			return "ATTR"
		elif tokens[1].name=="OPEN_P":
			return "FUNCTION_CALL"
		else :
			raise RuntimeError("Unexpected token",tokens[0])
	
	if tokens[0].name=="IF":return "IF"
	if tokens[0].name=="ELSE":return "ELSE"
	if tokens[0].name=="FOR":return "FOR"
	if tokens[0].name=="WHILE":return "WHILE"
	if tokens[0].name=="SWITCH":return "SWITCH"
	if tokens[0].name=="STOP":return "STOP"
	if tokens[0].name=="CASE":return "CASE"
	if tokens[0].name=="DEFAULT":return "DEFAULT"

	raise RuntimeError("Unexpected token",tokens[0])
	
class Token(namedtuple("Token",["name","value"])):
	def __str__(self):
		return f"<{self.name},{repr(self.value)}>"
	def __repr__(self):
		return str(self)
class Variable(namedtuple("Variable",["type","name"])):
	def __str__(self):
		return f"Variable({self.type},{repr(self.name)})"
	def __repr__(self):
		return str(self)
symtable={}

parser=ArgumentParser()
parser.add_argument("input",help="token.json file")
args=parser.parse_args()

with open(args.input) as f:
	tokens=[Token(*obj) for obj in json.load(f)["tokens"]]
tree={}
#phase 1
assert tokens[0].name=="SCRIPT_START"
tree["script_name"]=extract_str(tokens[1])
tokens=tokens[2:]
#phase 2
assert tokens[0].name=="VARS_BLOCK"
tokens=tokens[1:]
vars_block,tokens=split_tokens(tokens,"MAIN_START")
for command in split_tokens(vars_block,"END_BLOCK"):
	ids,vartype=split_tokens(command,"SEPARATOR")
	ids=list(split_tokens(ids,"COMMA"))
	assert len(vartype)==1
	vartype=vartype[0].value
	for tok in ids:
		assert len(tok)==1
		assert tok[0].name=="ID"
	ids=[tok[0] for tok in ids]
	
	for tok in ids:
		symtable[tok.value]=Variable(vartype,tok.value)
#phase 3
assert tokens[-1].name=="MAIN_END"
tokens=tokens[:-1]

print(symtable)

for command in split_tokens(tokens,"END_BLOCK","IF_END","FOR_END","WHILE_END","SWITCH_END"):
	# print(command)
	print(command_type(command))
