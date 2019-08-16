from lark import Visitor,Transformer,Token
def get_symtable(tree):
	assert tree.data=="start"
	visitor=SymtableVisitor()
	vars_block=tree.children[3]
	visitor.visit(vars_block)
	return visitor.symtable
def check_semantic(symtable,tree):
	assert tree.data=="start"
	main=tree.children[5]
	CheckIdsVisitor(symtable).visit(main)
	CheckExpsTransformer(symtable).transform(main)
def ptg2py(symtable,tree):
	return ptg2pyTransformer(symtable).transform(tree)
class SymtableVisitor(Visitor):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.symtable={
			"escreva":"function",
			"leia":"function"
		}
	def vars_block(self,tree):
		_type=tree.children[-1].value
		_vars=tree.children[:-1]
		for v in _vars:
			if self.symtable.get(v)!=None:
				raise SyntaxError(f"{v} is already defined")
			self.symtable[v.value]=_type

	def visit(self,tree):
		super().visit(tree)
class CheckIdsVisitor(Visitor):
	def __init__(self,symtable,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.symtable=symtable
	def __default__(self,tree):
		for t in (c for c in tree.children if type(c)==Token):
			if (t.type=="ID") and (self.symtable.get(t.value)==None):
				raise SyntaxError(f"id {t.value} is not defined!")
class CheckExpsTransformer(Transformer):
	def __init__(self,symtable,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.symtable=symtable
	def exp(self,args):
		if len(args)==1:
			t=args[0]
			if t.type == "STRING":
				return "caractere"
			elif t.type=="NUMBER":
				return "real"
			elif t.type=="ID":
				ans=self.symtable[t.value]
				if ans=="function":
					raise SyntaxError("Invalid expression : function inside expression")
				return ans
			raise SyntaxError("Invalid token for expression")
		if type(args[0])==Token:#parentesis exp
			return args[1]
		a,op,b=args
		if (a=="caractere") or (b=="caractere"):
			#if both a,b are string and operation is not adition or they are different and regardless of the operation
			if ((a==b) and op.value!="+") or (a!=b):
				raise SyntaxError(f"Error, operation {{string ({op.value}) non-string }} is invalid")
			return "caractere"
		elif (a in {"inteiro","real"}) or (b in {"inteiro","real"}): #this is always true
			if op.type not in {"BINOP","AROP"}:
				raise SyntaxError(f"Error, operation ({op.value}) invalid")
			return "real"
	def attribution(self,args):
		_id=args[0]
		exp_type=args[2]
		id_type=self.symtable[_id]
		if (id_type!="caractere") and (exp_type=="caractere"):
			raise SyntaxError("Can't assign non-string to string")
		if (id_type=="caractere") and (exp_type!="caractere"):
			raise SyntaxError("Can't assign string to non-string")

ptgtype2pytype={
	"caractere":"str",
	"real":		"float",
	"inteiro":	"int"
}
exp_hook={
	"^":"**",
	"e":"and",
	"ou":"or",
	"MOD":"%",
	"=":"=="
}
def tabulate(string):
	return "\n".join(["\t"+s for s in string.split("\n")[:-1]])+"\n"
class ptg2pyTransformer(Transformer):
	def __init__(self,symtable,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.symtable=symtable
	def _buildvars(self):
		ans=""
		for _var,_type in {k:v for k,v in self.symtable.items() if v!="function"}.items():
			ans+=(f"{_var}={ptgtype2pytype[_type]}()\n")
		return ans
	def start(self,args):
		label=f"#{args[1][1:-1]}\n"
		main=args[-2]
		return label+self._buildvars()+main
	def main(self,args):
		return "".join(args)
	def command(self,args):
		return "".join(args)
	def function_call(self,args):
		return "".join(args)
	def command_loop(self,args):
		return "".join(args)
	def command_conditional(self,args):
		return "".join(args)
	def if_body(self,args):
		if len(args)==0:
			return "pass\n"
		return tabulate("".join(args))
	def switch_body(self,args):
		return self.if_body(args)
	def for_body(self,args):
		return self.if_body(args)
	def while_body(self,args):
		return self.if_body(args)
	def attribution(self,args):
		_id=args[0]
		_exp=args[2]
		return f"{_id}={_exp}\n"
	def exp(self,args):
		if len(args)==3 and type(args[1])==Token:
			args[1]=exp_hook.get(args[1],args[1])
		return " ".join(args)
	def command_increment(self,args):
		if type(args[-1])!=Token:#if its not token then there is not a ++ token in the end
			return "".join(args)+"\n"
		return f"{args[0]}+=1\n"
	def stop(self,args):
		return args[0]+"\n"
	def function_print(self,args):
		return f"print({','.join(args)})\n"
	def function_scan(self,args):
		_id=args[0]
		_type=ptgtype2pytype[self.symtable[_id]]
		return f"{_id}={_type}(input())\n"
	def command_if(self,args):
		ans=f"if({args[1]}):\n{args[3]}"
		for i,t in enumerate(args[4:],4):
			if type(t)==Token and t.type=="ELSE":
				nt=args[i+1]
				if type(nt)==Token and nt.type=="IF":
					ans+=f"elif ({args[i+2]}):\n{args[i+4]}"
				else:
					ans+=f"else:\n{args[i+1]}"
		return ans
	def command_switch(self,args):
		_id=args[1]
		state=0
		ans=""
		for i,t in enumerate(args[2:],2):
			if type(t)==Token:
				if t.type=="CASE":
					body=args[i+2].split("\n")
					if body[-2].strip()!="pare":
						raise SyntaxError(f"switch case without break not implemented")
					del body[-2]
					body="\n".join(body)
					ans+=f"{['if','elif'][state]} {_id}==({args[i+1]}):\n{body}"
					state=1
				elif t.type=="DEFAULT":
					ans+=f"else:\n{args[i+1]}"
		return ans

	def command_for(self,args):
		_id=args[1]
		a,b,c=args[3:8:2]
		body=args[-2]
		return f"for {_id} in range({a},{b},{c}):\n{body}"
	def command_while(self,args):
		exp=args[1]
		body=args[-2]
		return f"while({exp}):\n{body}"
