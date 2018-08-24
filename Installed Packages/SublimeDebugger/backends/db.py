from .python3s_backend import DBPython3S
import threading
import time
import subprocess
import os
from .comm_utils import PingPong #Peer
import json
from zipfile import ZipFile

def Client(lang):
	return DB(lang) if lang != "python3s" else DBPython3S()

in_this_folder = lambda filename: os.path.abspath(os.path.dirname(os.path.abspath(__file__))+'/'+filename)

class DB():
	def __init__(self, lang):
		this = in_this_folder("..")
		alt  = in_this_folder("../../SublimeDebugger")
		isdir = os.path.isdir(this)
		if not isdir:
			ZipFile(this).extractall(path=alt)
		debugger_folder = this if isdir else alt
		try:
			cmds = json.load(open(debugger_folder+"/SublimeDebugger.sublime-settings"))
		except Exception as e:
			print(e)
			print("SublimeDebugger.sublime-settings not found")
		# print(cmds[lang], debugger_folder+"/backends/"+lang+"_server.py", os.path.isfile(debugger_folder+"/backends/"+lang+"_server.py"))
		self.sp = subprocess.Popen([cmds[lang], debugger_folder+"/backends/"+lang+"_server.py"])
		self.breakpoints = {}
		self.peer = SublimePeer()
		self.set_break    = self.peer.D_set_break
		self.clear_break  = self.peer.D_clear_break
		self.toggle_break = self.peer.D_toggle_break
		self.tryeval      = self.peer.D_tryeval
	def runscript(self, filename):
		self.peer.D_set_breakpoints(self.breakpoints)
		self.peer.D_runscript(filename)
	def set_parent(self,p):
		self.peer.parent = p
	def get_parent(self):
		return self.peer.parent
	def __del__(self):
		self.sp.kill()
		self.sp.terminate()
		pass
	parent = property(fset=set_parent, fget=get_parent)

class SublimePeer(PingPong):
	def E_get_cmd       (self, line,locals,globals,filename): return self.parent.get_cmd (line,locals,globals,filename)
	def E_set_break     (self, filename,line, bpinfo       ): self.parent.set_break      (filename,line,bpinfo)
	def E_clear_break   (self, filename,line               ): self.parent.clear_break    (filename,line)
	def E_toggle_break  (self, filename,line               ): self.parent.toggle_break   (filename,line)
	def E_show_help     (self, s                           ): self.parent.show_help      (s)
	def E_show_exception(self, s                           ): self.parent.show_exception (s)
	def E_finished      (self,                             ): self.parent.finished       ()	
