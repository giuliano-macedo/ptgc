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
def command_f(sub_tree):
	for command in (o.children[0] for o in main.children):
		command_hook[command.data](command)
def inorder(t):
	if type(t)==Token:
		if t.type=="BINOP" or t.type=="AROP":
			return exp_hook.get(t.value,t.value)
		return t.value
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
def attr_f(sub_tree):
	children=sub_tree.children
	write(f"{children[0].value}={exp_eval(children[-1])}\n")
def inc_f(sub_tree):
	children=sub_tree.children
	if children[-1].value!="++":
		write(f"{inorder(children)}\n")
	else:
		write(f"{children[0].value}+=1\n")
def function_f(sub_tree):
	f=sub_tree.children[0]
	if f.data=="function_print":
		exp=[c if type(c)==Token else exp_eval(c) for c in f.children]
		write(f"print({','.join(exp)})\n")
	else:
		write(f"{f.children[0]}=input()\n")
def conditionals_f(sub_tree):
	pass
def loops_f(sub_tree):
	pass
command_hook={
	"attribution"			:attr_f,
	"command_increment"		:inc_f,
	"stop"					:lambda s:None,
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
dot = Digraph(format="pdf")
build_dot(tree,dot)
dot.render('tree.dot')
write=lambda s:args.output.write(s)
write(f"#{tree.children[1].value[1:-1]}\n")
#vars
d={"caractere":"\"\"","real":".0","inteiro":"0"}
for var in tree.find_data("vars_block"):
	t=d[var.children[-1].value]
	_vars=var.children[:-1]
	write(f"{','.join(_vars)}={','.join([t]*len(_vars))}\n")
#----------------------------------------------------------------
main=tree.children[-2]
command_f(main)
# breakpoint()