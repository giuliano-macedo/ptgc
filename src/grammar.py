import re
import shlex
def _int(buff):
	return re.match("[0-9]",buff),None
def _str(buff):
	#TODO DOES NOT WORK WITH SCAPED STRING
	s=buff.split("\"")
	if len(s)==3:
		return True,s[1]
	return False,None
	
def _separator(buff):
	return buff==";",None
def _script_start(buff):
	return re.match("(algoritmo|algorítmo)",buff),None
def _var_block(buff):
	return re.match("variaveis",buff),None
def _main_block_start(buff):
	return re.match("inicio|início",buff),None
def _attr(buff):
	return re.match("<-",buff),None
def _main_block_end(buff):
	return re.match("fimalgoritmo",buff),None
def _id(buff):
	return True,buff
grammar={
	"int":_int,
	"str":_str,
	"separator":_separator,
	"script_start":_script_start,
	"var_block":_var_block,
	"main_block_start":_main_block_start,
	"attr":_attr,
	"main_block_end":_main_block_end,
	"id":_id,
}
if __name__=="__main__":
	print(_str("'hi'"))
	print(_str("'hi\\'"))
	print(_str("'hi\""))
