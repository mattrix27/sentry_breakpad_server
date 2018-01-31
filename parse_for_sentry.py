from raven import Client

class Module(object):
	def __init__(self, line):
		self.line = line
	def parse(self):
		return

class Frame(object):
	def __init__(self, lineno=None, filename=None, abs_path=None, function=None, modules = None):
		self.f_lineno = lineno
		self.filename = filename
		self.abs_path = abs_path
		self.function = function
		self.module = modules
		
class Breakpad_Sentry_Report(object):
	def __init__(self, client = None, extra = {}):
		self.extra = extra
		self.client = client

	def parse_breakpad_stack(self, stack_trace):
		mode = None
		curr_tag = None
		self.tags = {}
		self.threads = []
		self.modules = []
		self.modules_list = set()
		lineiterator = iter(stack_trace.splitlines())
		for line in lineiterator:
			if line:					
				if line.find("Thread") > -1:
					thread = ""
					mode = "thread"
					if line.find("crash") > -1:
						thread = "CRASH\n"
					
				elif line.find('module') > -1:
					mode = "module"

				else:
					if mode:
						if mode == "thread":
							thread += line+"\n"
						elif mode == "module":
							self.modules.append(Module(line).line)

							# m_index = line.find(".exe")
							# if m_index == -1:
							# 	m_index = line.find(".dll")

							# s = line[::-1].find(" ",len(line) - m_index)
							# self.modules_list.append(line[len(line)-s:m_index+4])

					else:
						index = line.find(':')
						if index != -1:
							if line[0 : index].lower() == "crash reason":
								self.message = line[(index+2):]
							else:
								curr_tag = line[0:index]
								self.tags[curr_tag] = line[(index+2):]
						else:
							if curr_tag:
								self.tags[curr_tag] += ", " + line.lstrip()
			else:
				if mode == "thread":
					self.threads.append(thread)
				mode = None

	def parse_threads(self):
		for num, thread in enumerate(self.threads):
			if thread.find("CRASH", 0, 10) > -1:
				self.parse_crashed_stacktrace(thread)
			self.extra["Thread " + str(num)] = thread

	def parse_crashed_stacktrace(self, thread):
		lineiterator = iter(thread.splitlines())
		self.crash_stack = []
		num = ['0','1','2','3','4','5','6','7','8,','9']
		file_ext = ['.h','.cpp','.py']
		filename, lineno, abs_path, function, module = None, None, None, None, None
		framed = False
		for line in lineiterator:
			if line.lstrip()[0] in num:
				if framed:
					self.crash_stack.append(Frame(lineno, filename, abs_path, function, module))
				framed = True
				m_index = line.find(".exe")
				if m_index == -1:
					m_index = line.find(".dll")
				if m_index != -1:
					module = line[(len(line) - (line[::-1].find(" ",len(line) - m_index))):m_index+4]
					self.modules_list.add(module)

					fun_ind = line.find("(", m_index+5)
					if fun_ind != -1:
						fun_endex = line.find(")", fun_ind)
						function = line[m_index+5:fun_endex]
						
						file_ind = line.find(".", fun_endex)
						if file_ind != -1:
							start = line.find('[', fun_endex)
							end = line.find(' ', file_ind)
							filename = line[start+1:end]
							abs_path = '/Users/matthew.tung/' + filename
							num_ind = line.find(":", end)
							if num_ind != -1:
								nu_line = line[num_ind+1:].lstrip()
								end = nu_line.find(" ")
								lineno = int(nu_line[:end])

	def upload(self):
		#TODO, change DSN
		#if not self.client:
		#	self.client = Client('https://2cfceaaa3e87496daa2ee59daf3cb7e8:da63b31a314d4fd1b31a9f9098392195@sentry.io/271949')
		#self.client.captureMessage(self.message, extra = self.extra, tags = self.tags, stack = self.crash_stack, sample_rate = 1)

		print(self.extra)
	
	def sentrify(self, dump_text):
		self.parse_breakpad_stack(dump_text)
		self.parse_threads()
		self.upload()


love = "AHHHHHH"

test = Breakpad_Sentry_Report()
test.parse_breakpad_stack(love)
test.parse_threads()
test.message = 'love'
test.extra["hey"] = "www.google.com"
test.crash_stack = None

# #TODO get our own DSN for brkpad.vivint.com
#client = Client('https://2cfceaaa3e87496daa2ee59daf3cb7e8:da63b31a314d4fd1b31a9f9098392195@sentry.io/271949')
#client = Client('http://7c85c3a768234aa682068d181d72f605:7a37600f8c094d93b1a7d1817776fa00@localhost:8000/2')
#client.captureMessage(test.message, extra = test.extra, tags = test.tags, stack = test.crash_stack, sample_rate = 1)



# if __name__== "__main__":
# 	print("hi")
# 	if len(sys.argv) == 2:
# 		try:
# 			love = subprocess.check_output(['breakpad/src/src/processor/minidump_stackwalk', sys.argv[1] + '.dmp', '/Users/matthew.tung/breakpad/src/src/processor/testdata/symbols/'])
# 			print(love)
# 			test = Breakpad_Sentry_Report()
# 			test.parse_breakpad_stack(love)
# 			test.parse_threads()
# 		except:
# 			print("this aint a dump")
		
# 	elif len(sys.argv) == 1:
# 		print("You didn't give a dump :(")
# 	else:
# 		print("AHHH, too many dumps, this is not supported yet")