# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import os

from subprocess import Popen, PIPE
import subprocess


PYTHONEXE = "D:\\Anaconda3\\python.exe "
def python_exec(pyfile):
	p = os.environ.get('PYTHONPATH')
	pp = os.environ.get('PYTHON_PATH')
	print ('"' + PYTHONEXE + ' ' + pyfile +'"')
	exec ('"' + PYTHONEXE + ' ' + pyfile +'"')
	pass

def process_exec(pyfile):
	

	commande = ["echo", u"Hello World!"]
	#commande = [PYTHONEXE, pyfile]
	
	out = Popen(commande, stdout=PIPE)
	#subprocess.call(commande)
	#subprocess.check_output(commande)
	
	(sout,serr)=out.communicate()
	print (sout)	
	print (serr)

	pass





def python_eval(result):

	var = eval(result)
	print(var)
	pass 



if __name__ == "__main__":
	
	process_exec("D:/WORK/docutone/python/src/analyse/legal_term.py")
