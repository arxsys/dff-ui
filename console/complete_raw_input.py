# DFF -- An Open Source Digital Forensics Framework
# Copyright (C) 2009-2013 ArxSys
# This program is free software, distributed under the terms of
# the GNU General Public License Version 2. See the LICENSE file
# at the top of the source tree.
#  
# See http://www.digital-forensic.org for more information about this
# project. Please do not directly contact any of the maintainers of
# DFF for assistance; the project provides a web site, mailing lists
# and IRC channels for your use.
# 
# Author(s):
#  Solal Jacob <sja@digital-forensic.org>
#  Frederic Baguelin <fba@digital-forensic.org>
#

import sys,os, string, struct, types, unicodedata, platform

if os.name == "posix":
  import tty, termios, fcntl
elif os.name == "nt":
  import msvcrt
  from ctypes import windll, create_string_buffer

from dff.ui.history import history

def get_term_size():
  if os.name == "posix":
    width = 80
    s = struct.pack('HHHH', 0, 0, 0, 0)
    s = fcntl.ioctl(1, termios.TIOCGWINSZ, s)
    twidth = struct.unpack('HHHH', s)[1]
    if twidth > 0:
      width = twidth
    return width
  elif os.name == "nt":
    h = windll.kernel32.GetStdHandle(-12)
    csbi = create_string_buffer(22)
    res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
    if res:
      (bufx, bufy, curx, cury, wattr, left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
      sizex = right - left + 1
    else:
      sizex = 80
    return sizex    	

# The following function comes from http://bugs.python.org/issue12568#msg155361
# It is used because there is currently no way to determine character width (in terms
# of columns length when printed) by default in Python
def wcwidth(c, legacy_cjk=False):
  if c in u'\t\r\n\10\13\14': raise ValueError('character %r has no intrinsic width' % c)
  if c in u'\0\5\7\16\17': return 0
  if u'\u1160' <= c <= u'\u11ff': return 0 # hangul jamo
  if unicodedata.category(c) in ('Mn', 'Me', 'Cf') and c != u'\u00ad': return 0 # 00ad = soft hyphen
  eaw = unicodedata.east_asian_width(c)
  if eaw in ('F', 'W'): return 2
  if legacy_cjk and eaw == 'A': return 2
  return 1

def wcstr_width(buff, legacy_cjk=False):
  buff = unicode(buff, 'utf-8', 'replace') if type(buff) == types.StringType else buff
  width = 0
  for c in buff:
    try:
      width += wcwidth(c, legacy_cjk)
    except ValueError:
      pass
  return width


class complete_raw_input():
   class __posix():
     eol = "\n"
     MOVE_LEFT = '\x1b\x5b\x44'
     MOVE_RIGHT = '\x1b\x5b\x43'
     MOVE_UP = '\x1b\x5b\x41'
     MOVE_DOWN = '\x1b\x5b\x42'
     BACKSPACE = '\b'
     DEL = '\x7f'
     START = '\x1b\x5b\x48'
     END = '\x1b\x5b\x46'
     CLS = '\x0c'
     CUT = '\x0b'
     PASTE = '\x19'
     CTRL_LEFT = '\x1b\x5b\x31\x3b\x35\x44'
     CTRL_RIGHT = '\x1b\x5b\x31\x3b\x35\x43'
     PG_UP = '\x1b\x5b\x35\x7e'
     PG_DOWN = '\x1b\x5b\x36\x7e'

     def __init__(self, parent, console):
       self.console = console	
       self.completekey = self.console.completekey
       self.complete_func = self.console.complete
       self.line = u""
       self.cutbuff = u""
       self.history = history()
       self.parent = parent
       self.fd = sys.stdin.fileno()
       if os.isatty(self.fd):
         self.oldterm = termios.tcgetattr(self.fd)
         self.term = termios.tcgetattr(self.fd)
         self.term[3] = self.term[3] & ~termios.ICANON & ~termios.ECHO
         

     def cfmakeraw(self):
       pass

     def get_term_size(self):
       return get_term_size()


     def get_char(self, timeout = 0):
       ch = '' 
       if os.isatty(self.fd):
	 if not timeout:
           self.term[6][termios.VMIN] = 1
           self.term[6][termios.VTIME] = timeout
	 else:
           self.term[6][termios.VMIN] = 0 
           self.term[6][termios.VTIME] = timeout
         try :
           termios.tcsetattr(self.fd, termios.TCSANOW, self.term)
           if platform.system().find('BSD') == -1:
# Fix for BSD, avoid sendbreack : termios.error: (25, 'Inappropriate ioctl for device')
             termios.tcsendbreak(self.fd, 0)
	   try :
	     ch = os.read(self.fd, 4096)
	   except OSError:
	     pass
         finally :
	   termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.oldterm)
       else: 
	  try :
            ch = os.read(self.fd, 4096)
	  except OSError:
            pass
       if ch == self.BACKSPACE or ch == self.DEL:
         self.delchar()
       elif ch in [self.MOVE_LEFT, self.MOVE_RIGHT, self.END, self.START]:
         self.moveCursor(ch)
       elif ch == self.MOVE_UP:
	   self.clear_line()
	   cmd = self.history.getprev()
	   if cmd:
             self.insert_text(unicode(cmd, 'utf-8', 'replace') if type(cmd) == types.StringType else cmd)
       elif ch == self.MOVE_DOWN:
	   self.clear_line()
           cmd = self.history.getnext()
	   if cmd:
	    self.insert_text(unicode(cmd, 'utf-8', 'replace') if type(cmd) == types.StringType else cmd)
       elif ch == self.CUT:
         self.cut()
       elif ch == self.PASTE:
         self.insert_text(self.cutbuff)
       else:
         return unicode(ch, 'utf-8', 'replace') if type(ch) == types.StringType else ch
       return None	

     def __getattr__(self, attr):
	return getattr(self.parent, attr)

   class __nt():
     eol = "\r"
     CODE_LEFT = '\x4b'
     MOVE_LEFT = '\x08'
     MOVE_RIGHT = '\x4d'
     MOVE_UP = '\x48'
     MOVE_DOWN = '\x50'
      
     def __init__(self, parent, console):
       self.console = console
       self.completekey = self.console.completekey
       self.complete_func = self.console.complete
       self.line = u""
       self.history = history()
       self.parent = parent

     def get_term_size(self):
       return get_term_size()

     def get_char(self, timeout = None):
       ch = msvcrt.getch()      
       if len(ch) == 1:
         if ch in string.printable:
           return ch
         elif ch == '\x08':
           self.delchar() 		 
   	 elif ch == '\xe0':
          ch = msvcrt.getch()
          if ch == self.CODE_LEFT: 
            if self.cursor > 0:
	      self.print_text(self.MOVE_LEFT)	
	      self.cursor -= 1	
          elif ch == self.MOVE_RIGHT:
            if self.cursor < len(self.line):
	      pad = len(self.line) - self.cursor
	      self.print_text(self.line[self.cursor:] + (pad - 1) * self.MOVE_LEFT)
	      self.cursor += 1
          elif ch == self.MOVE_UP:
	      self.clear_line()
	      cmd = self.history.getnext()
	      if cmd:
                self.insert_text(unicode(cmd, 'utf-8', 'replace') if type(cmd) == types.StringType else cmd)
          elif ch == self.MOVE_DOWN:
	      self.clear_line()
              cmd = self.history.getprev()
	      if cmd:
	        self.insert_text(unicode(cmd, 'utf-8', 'replace') if type(cmd) == types.StringType else cmd)
          return None

     def __getattr__(self, attr):
	return getattr(self.parent, attr)

   def __init__(self, console):
	if os.name == "posix":
	  complete_raw_input.__instance = complete_raw_input.__posix(self, console)
  	elif os.name == "nt":
	  complete_raw_input.__instance = complete_raw_input.__nt(self, console)
 
   def __setattr__(self, attr, value):
	setattr(self.__instance, attr, value)
  
   def __getattr__(self, attr):
	return getattr(self.__instance, attr)

   def wait(self, timeout = None):
    c = None 
    self.line = u""
    self.cursor = 0
    c = self.get_char()			  
    if c == 'z':
	return "signal get"
    return  "loop"


   def raw_input(self):
    c = None 
    self.line = u""
    self.cursor = 0
    sys.__stdout__.write(self.console.prompt)
    sys.__stdout__.flush()
    while c != self.eol:
       if c:
         if c == self.completekey:
           spaceidx = self.line[:self.cursor].rfind(" ")
           if spaceidx != -1:
             text = self.line[spaceidx+1:self.cursor]
           else:
             text = self.line[:self.cursor]
           i = 0
           skey = 0
           kshell = False
           while i != len(text):
             if text[i] in [";", "<", ">", "&", "|"]:
               kshell = True
               skey = i
             i += 1
           if kshell:
             text = text[skey+1:]
           matches = self.complete_func(self.line, self.cursor)
           self.insert_comp(text, matches)
         else:
	   self.insert_text(c)
       c = self.get_char()			   
    self.print_text('\n')
    return self.line


   def insert_text(self, text):
       lsplit = u""
       rsplit = u""
       lpos = 0
       if self.cursor > 0:
         if self.cursor != len(self.line):
           lpos = self.cursor
           rsplit = self.line[lpos:]
           lsplit = self.line[:lpos]
         else:
           lsplit = self.line
           rsplit = u""
           lpos = self.cursor - 1
       self.line = lsplit + text + rsplit
       self.cursor = len(lsplit) + len(text)
       sys.__stdout__.write(text + rsplit)
       sys.__stdout__.write(len(rsplit.encode('utf-8')) * self.MOVE_LEFT)
       sys.__stdout__.flush()


   def print_text(self, text): 
       sys.__stdout__.write(text)
       sys.__stdout__.flush()	


   def clear_line(self):
      line_len = wcstr_width(self.line)
      self.print_text(self.MOVE_LEFT * line_len + " " * line_len + line_len * self.MOVE_LEFT)
      self.line = u''
      self.cursor = 0	


   def cut(self):
     rsplit = u""
     if self.cursor > 0:
       if self.cursor != len(self.line):
         rsplit = self.line[self.cursor:]
         self.line = self.line[:self.cursor]
     else:
       rsplit = self.line
       self.line = u""
       self.cursor = 0
     self.cutbuff = rsplit
     removal = wcstr_width(self.cutbuff)
     self.print_text(" " * removal + self.MOVE_LEFT * removal)


   def moveCursor(self, _type):
     if _type == self.MOVE_LEFT: #left arrow
       if self.cursor > 0:
         offset = wcstr_width(self.line[self.cursor-1])
         self.print_text(self.MOVE_LEFT*offset)
         self.cursor -= 1
     elif _type == self.MOVE_RIGHT:
       if self.cursor < len(self.line):
         offset = wcstr_width(self.line[self.cursor])
         self.print_text(self.MOVE_RIGHT*offset)
         self.cursor += 1
     else:
       loffset = 0
       roffset = 0
       if self.cursor > 0:
         if self.cursor != len(self.line):
           loffset = wcstr_width(self.line[:self.cursor])
           roffset = wcstr_width(self.line[self.cursor:])
         else:
           loffset = wcstr_width(self.line)
       else:
         roffset = wcstr_width(self.line)
       if _type == self.END:
         self.cursor = len(self.line)
         self.print_text(self.MOVE_RIGHT*roffset)
       if _type == self.START:
         self.cursor = 0
         self.print_text(self.MOVE_LEFT*loffset)


   def delchar(self):
       lsplit = u""
       rsplit = u""
       lpos = 0
       if self.cursor > 0:
         if self.cursor != len(self.line):
           lpos = self.cursor - 1
           lsplit = self.line[:lpos]
           rsplit = self.line[lpos+1:]
         else:
           lsplit = self.line[:-1]
           rsplit = u""
           lpos = self.cursor - 1
         removal = wcstr_width(self.line[lpos])
         self.cursor -= 1
         self.line = lsplit + rsplit
         len_rsplit = 0
         rsplit += " "
         len_rsplit += wcstr_width(rsplit)
         self.print_text(self.MOVE_LEFT * removal + rsplit + self.MOVE_LEFT * len_rsplit)


   def insert_comp(self, text, matches):
     #results of completion with lots of information
     res = ""
     if isinstance(matches, dict) and matches["matched"] != 0:
       if matches["matched"] > 1:
         sys.stdout.write("\n")
       if "type" in matches:
         if hasattr(self.console.completion, "insert_" + matches["type"] + "_comp"):
           func = getattr(self.console.completion, "insert_" + matches["type"] + "_comp")
           res = func(text, matches)
         else:
           pass
       else:
         pass

     if isinstance(matches, str):
       start = len(text)
       if start > 0:
          ins = matches[start:]
       else:
         ins = matches
       self.line = self.line[:self.cursor] + ins + self.line[self.cursor:]
       self.cursor += len(ins)

     if res != "" and res != None:
       self.line = self.line[:self.cursor] + res + self.line[self.cursor:]
       self.cursor += len(res)

     n = len(self.line) - self.cursor
     sys.stdout.write("\n" + self.console.prompt)
     self.print_text(self.line + n * self.MOVE_LEFT)
