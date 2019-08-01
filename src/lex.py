import json
import re
from argparse import ArgumentParser
from itertools import chain,tee
import itertools
import ox
from os import remove

quote=r"(\'|\")"
char=r"[a-zA-z]"
integer=r"(\+|\-|)\d+"
float_classic=rf"{integer}(\.\d*)"
float_e=rf"({float_classic}|{integer})((e|E)({float_classic}|{integer}))?"
tokens=[
	('SCRIPT_START', r'algor(i|í)tmo'),
	("STRING",rf"{quote}.*{quote}"), #does not work with scaped string
	('VARS_BLOCK', r'vari(a|á)veis'),
	('COMMA', r'\,'),
	('SEPARATOR', r'\:'),
	('TYPE', r'real|inteiro|caractere'),
	("END_BLOCK",r";"),
	("MAIN_START",r"in(i|í)cio"),
	("MAIN_END",r"fimalgor(i|í)tmo"),
	("ATTR",r"<-"),
	("AROP",r"\+|\-|\*|\/"),
	("NUMBER",rf"{float_classic}|{float_e}"),
	("ID",rf"{char}\w*"),
]

parser=ArgumentParser()
parser.add_argument("input",help="source file")
args=parser.parse_args()

with open(args.input,encoding="utf-8") as f:
	lexer = ox.make_lexer(tokens)
	out=[(obj.type,obj.value) for obj in lexer(f.read())]
print(json.dumps(out,indent=4,ensure_ascii=False))
with open("tokens.json","w") as f:
	json.dump({"tokens":out},f,indent=4,ensure_ascii=False)
# lexer() creates this 2 files for some reason
remove("parsetab.py")
remove("parser.out")