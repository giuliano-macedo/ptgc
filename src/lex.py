import re
from argparse import ArgumentParser
from itertools import chain,tee
import itertools
import ox
from os import remove
import json

quote=r"(\'|\")"
char=r"[a-zA-Z]"
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
	("OPEN_P",r"\("),
	("CLOSE_P",r"\)"),
	("ELSE",r"sen(a|ã)o"),
	("IF",r"se"),
	("THEN",r"ent(a|ã)o"),
	("IF_END",r"fimse"),
	("FOR",r"para"),
	("FROM",r"de"),
	("UNTIL",r"at(e|é)"),
	("STEP",r"passo"),
	("DO",r"fa(c|ç)a"),
	("FOR_END",r"fimpara"),
	("WHILE",r"enquanto"),
	("WHILE_END",r"fimenquanto"),
	("SWITCH",r"escolha"),
	("DEFAULT",r"casopadr(a|ã)o"),
	("CASE",r"caso"),
	("STOP",r"pare"),
	("SWITCH_END","fimescolha"),
	("ATTR",r"<-"),
	("AROP",r"\+|\-|\*|\/|MOD|\^"),
	("BINOP",r"\>|\>\=|\<|\<\=|\=|\!\="),
	("NUMBER",rf"{float_classic}|{float_e}"),
	("ID",rf"{char}\w*"),
]

parser=ArgumentParser()
parser.add_argument("input",help="source file")
args=parser.parse_args()

with open(args.input,encoding="utf-8") as f:
	lexer = ox.make_lexer(tokens)
	_err=None
	try:
		out=[(obj.type,obj.value) for obj in lexer(f.read())]
	except Exception as e:
		_err=e
	#lexer() create this 2 files for some reason
	try:
		remove("parsetab.py")
		remove("parser.out")
	except Exception:pass
	if _err:
		raise _err
with open("tokens.json","w") as f:
	f.write("{\"tokens\":[\n")
	json_str=lambda s:json.dumps(s,ensure_ascii=False)
	for token_name,token_value in out:
		f.write(f"\t[{json_str(token_name)},{json_str(token_value)}],\n")
	if len(out)!=0:
		f.seek(f.tell()-2)
	f.write("\n]}")