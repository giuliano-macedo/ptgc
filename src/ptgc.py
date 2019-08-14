from lark import Lark,Token
from graphviz import Digraph
import argparse
def build_dot(tree,dot):
	h=str(id(tree))
	label=getData(tree) if istoken(tree) else f"<<font face=\"boldfontname\">{getData(tree)}</font>>"
	dot.node(h,label=label)
	if istoken(tree):
		return 
	for children in tree.children:
		dot.edge(h,str(id(children)))
		build_dot(children,dot)
def check_ids(t):
	if type(t)!=Token:
		for c in t.children:
			check_ids(c)
		return
	if t.type!="ID":
		return
	if symtable.get(t.value)==None:
		raise SyntaxError(f"id {t.value} is not defined!")
def command_f(sub_tree,tab=0):
	for command in (o.children[0] for o in sub_tree.children):
		command_hook[command.data](command,tab)

def inorder(t):
	if type(t)==Token:
		return exp_hook.get(t.value,t.value)
	ans=[]
	for c in t.children:
		ans.append(inorder(c))
	return " ".join(ans)
exp_hook={
	"^":"**",
	"e":"and",
	"ou":"or",
	"MOD":"%",
	"=":"=="
}
def exp_eval(sub_tree):
	return inorder(sub_tree)
def attr_f(sub_tree,tab):
	children=sub_tree.children
	write(f"{children[0].value}={exp_eval(children[-1])}\n",tab)
def inc_f(sub_tree,tab):
	children=sub_tree.children
	if children[-1].value!="++":
		write(f"{inorder(children)}\n",tab)
	else:
		write(f"{children[0].value}+=1\n",tab)
def function_f(sub_tree,tab):
	f=sub_tree.children[0]
	if f.data=="function_print":
		exp=[c if type(c)==Token else exp_eval(c) for c in f.children]
		write(f"print({','.join(exp)})\n",tab)
	else:
		write(f"{f.children[0]}=input()\n",tab)
def conditionals_f(sub_tree,tab):
	conditional=sub_tree.children[0]
	children=conditional.children
	if conditional.data=="command_if":
		write(f"if ({exp_eval(children[1])}):\n",tab)
		command_f(children[3],tab+1)

		for i,c in enumerate(children[4:],4):
			if type(c)!=Token:
				continue
			if c.type=="ELSE":
				if type(children[i+1])==Token:
					write(f"elif ({exp_eval(children[i+2])}):\n",tab)
					command_f(children[i+4],tab+1)
				else:
					write("else\n",tab)
					command_f(children[i+1],tab+1)
	elif conditional.data=="command_switch":
		_id=children[1].value
		numbers_if=0
		for i,c in enumerate(children):
			if type(c)!=Token:
				continue
			if c.type=="CASE":
				write(f"{['if','elif'][numbers_if>0]} {_id}==({exp_eval(children[i+1])}):\n")
				command_f(children[i+2],tab+1)
				try:
					assert children[i+2].children[-1].children[0].data == "stop"
				except Exception as e:
					breakpoint()
					raise SyntaxError(f"switch case without break not implemented")
					raise e
				numbers_if+=1



		
def loops_f(sub_tree,tab):
	conditional=sub_tree.children[0]
	children=conditional.children
	if conditional.data=="command_while":
		write(f"while ({exp_eval(children[1])}):\n",tab)
		command_f(children[3],tab+1)
	elif conditional.data=="command_for":
		write(f"for {children[1].value} in range({','.join([exp_eval(c) for c in children[3:8:2]] )})\n",tab)
		command_f(children[-2],tab+1)
command_hook={
	"attribution"			:attr_f,
	"command_increment"		:inc_f,
	"stop"					:lambda s,t:None,
	"function_call"			:function_f,
	"command_conditional"	:conditionals_f,
	"command_loop"			:loops_f,
}

istoken=lambda obj:type(obj)==Token
getData=lambda obj:obj if istoken(obj) else obj.data

parser=argparse.ArgumentParser()
parser.add_argument("input",type=argparse.FileType("r"))
parser.add_argument("-O","--output",type=argparse.FileType("w"),default="out.py")
args=parser.parse_args()

with open("grammar.lark") as f:
	lark=Lark(f.read())
tree=lark.parse(args.input.read())
main=tree.children[-2]
dot = Digraph(format="pdf")
build_dot(tree,dot)
dot.render('tree.dot')
def write(s,tab=0):
	args.output.write(("\t"*tab)+s)
write(f"#{tree.children[1].value[1:-1]}\n")
#vars
d={
	"caractere":"str()",
	"real":		"float()",
	"inteiro":	"int()"
}
symtable={"escreva":"function","leia":"function"}
for var in tree.find_data("vars_block"):
	_type=var.children[-1].value
	t=d[_type]
	_vars=var.children[:-1]
	for v in _vars:
		if symtable.get(v)!=None:
			raise SyntaxError(f"{v} is already defined")
		symtable[v]=_type
	write(f"{','.join(_vars)}={','.join([t]*len(_vars))}\n")
check_ids(main)
#----------------------------------------------------------------
command_f(main)
# breakpoint()