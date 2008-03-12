### Dstat most expensive process plugin
### Displays the name of the most expensive process
###
### Authority: dag@wieers.com

global string
import string

class dstat_topcpu(dstat):
    def __init__(self):
        self.name = 'most expensive'
        self.format = ('s', 16, 0)
        self.nick = ('cpu process',)
        self.vars = self.nick
        self.pid = str(os.getpid())
        self.cn1 = {}; self.cn2 = {}; self.val = {}

    def extract(self):
        self.val['max'] = 0.0
        for pid in os.listdir('/proc/'):
            try:
                ### Is it a pid ?
                int(pid)

                ### Filter out dstat
                if pid == self.pid: continue

                ### Using dopen() will cause too many open files
                l = string.split(open('/proc/%s/stat' % pid).read())
                if len(l) < 15: continue

                ### Reset previous value if it doesn't exist
                if not self.cn1.has_key(pid):
                    self.cn1[pid] = 0

                self.cn2[pid] = int(l[13]) + int(l[14])
                usage = (self.cn2[pid] - self.cn1[pid]) * 1.0 / tick

                ### Is it a new topper ?
                if usage < self.val['max']: continue

                ### Extract name
                name = l[1][1:-1]

                ### Get commandline
                m = string.split(open('/proc/%s/cmdline' % pid).read(), '\0')
                if len(m) > 1:
                    cmd = os.path.basename(m[1])

            except ValueError:
                continue
            except IOError:
                continue

            self.val['cmd'] = cmd
            self.val['max'] = usage
            self.val['name'] = name
            self.val['pid'] = pid
#            st = os.stat("/proc/%s" % pid)
#            if st:
#                pw = pwd.getpwuid(st.st_uid)
#                if pw:
#                    self.val['user'] = pw[0]
#                else:
#                    self.val['user'] = stat.st_uid
#            else:
#                self.val['user'] = 'none'

        if self.val['max'] == 0.0:
            self.val['process'] = ''
        else:
            ### If the name is a known interpreter, take the second argument from the cmdline
            if self.val['name'] in ('bash', 'csh', 'ksh', 'perl', 'python', 'sh'):
                self.val['process'] = self.val['cmd']
            else:
                self.val['process'] = self.val['name']

#               l = l.reverse()
#               for x in l:
#                   print x
#                   if x[0] != '-':
#                       self.val['name'] = os.path.basename(x)
#                       break

            ### Debug (show PID)
#           self.val['process'] = '%*s %-*s' % (5, self.val['pid'], self.format[1]-6, self.val['name'])

        if step == op.delay:
            self.cn1.update(self.cn2)

    def show(self):
        if self.val['max'] == 0.0:
            return '%-*s' % (self.format[1], '')
        else:
            return '%s%-*s%s' % (ansi['default'], self.format[1]-3, self.val['process'][0:self.format[1]-3], cprint(self.val['max'], ('p', 3, 34)))

    def showcsv(self):
        return '%s / %d%%' % (self.val['name'], self.val['max'])

# vim:ts=4:sw=4:et