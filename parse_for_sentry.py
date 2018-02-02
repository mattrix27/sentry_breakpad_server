#ALRIGHT, well this is a long one and definitely should be the one to change if you're getting stuff on sentry but it doesn't look like/how what you want. It basically takes a stack trace from breakpad, goes through and tries to pick pieces and put them in the right place

from raven import Client

#module class for modules, doesn't have like ANY purpose right now but it might be helpful or something if there's something more you to do when displaying modules used
class Module(object):
        def __init__(self, line):
                self.line = line
        def parse(self):
                return

#frame class for thread, holds info about them. Like modules, how or if this is used is up to you, feel free to work this out. The intended purpose would be if you had source code so it would be helpful to contain and use this class when going to source code and showing where error occured or something
class Frame(object):
        def __init__(self, lineno=None, filename=None, abs_path=None, function=None, modules = None):
                self.f_lineno = lineno
                self.filename = filename
                self.abs_path = abs_path
                self.function = function
                self.module = modules

#alright, the meat and potatos, let's go!
class Breakpad_Sentry_Report(object):

        #initates it, gives you a blank dictionary for 'extra' info that sentry displays and if you have a different projects on Sentry, then you can put in the corresponding client. Right now, I just make a default one below for demo purposes
        def __init__(self, client = None, extra = {}):
                self.extra = extra
                self.client = client

        #main function that goes through stack, it's pretty NOT flexible, so if it turns out your stack traces looks different from the ones I've seen, or you just want to make it more robust, then you'll definitely have to change
        def parse_breakpad_stack(self, stack_trace):
                mode = None
                curr_tag = None
                self.tags = {}
                self.threads = []
                self.modules = []
                self.modules_list = set()
                lineiterator = iter(stack_trace.splitlines())
                #splits stack trace into lines and goes through each
                for line in lineiterator:
                        if line:                                #checks to make sure it's just not white space
                                if line.find("Thread") > -1:    #if it sees thread goes into 'thread' mode to then start putting that in the right place
                                        thread = ""
                                        mode = "thread"
                                        if line.find("crash") > -1: #if it sees crash in the same line, it indicates that this is the main thread in which the code crashed, so note that
                                                thread = "CRASH\n"

                                elif line.find('module') > -1:  #if it sees module it goes into 'module' mode to also parse thos right
                                        mode = "module"

                                else:                           #when it neither, so it most likely just a line with actual info
                                        if mode:                #if a mode is active then it's 'suppposedly' a line with info corresponding with the that type of thingy
                                                if mode == "thread":
                                                        thread += line+"\n"	 #adds the line to the thread right
                                                elif mode == "module":           #alright so this part doesn't do anything special right now but it can, right not it just adds the line, but the module class has been made if you want there to be more to it
                                                        self.modules.append(Module(line).line)

                                                        # m_index = line.find(".exe")
                                                        # if m_index == -1:
                                                        #	m_index = line.find(".dll")

                                                        # s = line[::-1].find(" ",len(line) - m_index)
                                                        # self.modules_list.append(line[len(line)-s:m_index+4])

                                        else:                   #its not part of a thread or a module statement! configured to treat them as overview info and puts them as a 'tag' in sentry
                                                index = line.find(':') #finds the colon, as that usually indicates a thing, and its info i guess, so a new tag is made

                                                if index != -1:
                                                        #if the lines says crash reason, then set that info as the 'message' part in sentry. IMPORTANT: This is the 'title' of the error in Sentry (which is helpful because you can sort by frequency in the title very easily in Sentry) so please edit if that's not what you want
                                                        if line[0 : index].lower() == "crash reason":
                                                                self.message = line[(index+2):]

                                                        #creates a new tag and put the corresponding data
                                                        else:
                                                             	curr_tag = line[0:index]
                                                                self.tags[curr_tag] = line[(index+2):]

                                                #if there's a tag being worked on, this is to account if there is more than one line of info to said tag
                                                else:
                                                     	if curr_tag:
                                                                self.tags[curr_tag] += ", " + line.lstrip()

                        #if we're in thread mode, whitespace looks to indicate the end of the thread, so it turns thread mode off and appends the current thread to the list of threads
                        else:
                             	if mode == "thread":
                                        self.threads.append(thread)
                                mode = None

        #function to parse the threads put in self.threads from parse_breakpad_stack()
        def parse_threads(self):
                #goes through threads in the list
                for num, thread in enumerate(self.threads):
                        if thread.find("CRASH", 0, 10) > -1:    #if it has 'CRASH' on the top, which we note above, the call the helper function for this main partcular thread
                                self.parse_crashed_stacktrace(thread)
                        self.extra["Thread " + str(num)] = thread	#Put the thread in extra dict to display
			
        def parse_crashed_stacktrace(self, thread):
                lineiterator = iter(thread.splitlines())
                self.crash_stack = []
                num = ['0','1','2','3','4','5','6','7','8,','9']
                file_ext = ['.h','.cpp','.py']
                filename, lineno, abs_path, function, module = None, None, None, None, None
                framed = False

                #goes through each line in thread. NOTE: this is pretty sloppy and not very robust so depending on how your stack trace is formatted this could easily break, needed only if you want to show where in the source code the crash occurred so yeah
                for line in lineiterator:

                        #if the line starts with a number, then it's a new frame in the thread
                        if line.lstrip()[0] in num:
                                #appends the frame if there was one you were already working on
                                if framed:
                                        self.crash_stack.append(Frame(lineno, filename, abs_path, function, module))
                                framed = True

                                #goes through the line to get the file of the code or module, then the name of the function where it crashed, the filename, the path, and the line number. It's pretty ugly
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

        #gets the Sentry client and sends it up to Sentry!
        def upload(self, DSN):
                #TODO, change DSN
                if not DSN:
                        self.client = Client('https://86a27c24921747f89b0810d54436b876:321ab1800879441f82c9ac8303bb5254@brkpad.vivint.com/5') #test DSN to change!
                else:
                     	self.client = Client(DSN)
                self.client.captureMessage(self.message, extra = self.extra, tags = self.tags, sample_rate = 1)
                #print(self.extra)

        #Encapsulates all functions for use in other scripts
        def sentrify(self, dump_text, DSN=None):
                self.parse_breakpad_stack(dump_text)
                self.parse_threads()
                self.upload(DSN)



