from lark import Lark,Token
import graphviz
import argparse
from core import get_symtable,check_semantic,ptg2py	

class Lark2Graphviz(graphviz.Digraph):
	def __init__(self,tree,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.__build_dot(tree)
	def __build_dot(self,tree):
		istoken=lambda obj:type(obj)==Token
		getData=lambda obj:obj if istoken(obj) else obj.data
		h=str(id(tree))
		label=getData(tree) if istoken(tree) else f"<<font face=\"boldfontname\">{getData(tree)}</font>>"
		self.node(h,label=label)
		if istoken(tree):
			return 
		for children in tree.children:
			self.edge(h,str(id(children)))
			self.__build_dot(children)


parser=argparse.ArgumentParser()
parser.add_argument("input",type=argparse.FileType("r"))
parser.add_argument("-o","--output",type=argparse.FileType("w"),default="out.py")
args=parser.parse_args()

with open("grammar.lark") as f:
	lark=Lark(f.read())
tree=lark.parse(args.input.read())
Lark2Graphviz(tree,format="pdf").render("tree.dot")
symtable=get_symtable(tree)
check_semantic(symtable,tree)
args.output.write(ptg2py(symtable,tree))