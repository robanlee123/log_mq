#!/usr/bin/env python
 
import os, sys, time, signal, re, argparse, zmq, tailer, msgpack
from daemon import Daemon

logFile = '/var/log/logmq.log'
pidFile = '/var/run/logmq.pid'
conFile = '/etc/logmq.conf'
pidList = {}
confArr = []
stopTag = False


class LogTailer:
    def __init__(self, alog_file, host, port):
        """constructor for LogTailer"""
        self.alog_file = alog_file
        self.host = host
        self.port = port

        # zmq
        context = zmq.Context()
        sender = context.socket(zmq.PUSH)
        sender.setsockopt(zmq.HWM, 10000)
        sender.bind("tcp://" + host + ":" + str(port))
        self.sender = sender

    def follow(self):

        for line in tailer.follow(self.alog_file):
            if line.strip():
                self.sender.send(msgpack.packb(line.strip()))


def logmq(ip, port, logfile):
    """
    start access_log zmq bind
    """
    pid = os.fork()
    if pid != 0:
        pidList[pid] = [ip, port, logfile];
        return pid 
    else:
        t = LogTailer(logfile, ip, port)
        t.follow()
        os._exit(0)


def conf_parser(conf_file):
    """
    parser config file
    """
    confArr = []
    fh = file(conf_file, 'r')
    lines = fh.readlines()
    for line in lines:
        if not re.match(ur"^(#|//)", line):
            confEle = line.strip('\n').split(" ")
            if confEle[0] and confEle[1] and confEle[2]:
                confArr.append([confEle[0], confEle[1], confEle[2]])
    fh.close()
    return confArr

def reload(signum, frame):
    if os.getppid() == 1:
        confArr = conf_parser(conFile)
        print "[reload] [%d] %s" % (os.getpid(), confArr)

def term(signum, frame):
    """
    stop program, only parrent process do this
    """
    stopTag = True
    ppid = os.getppid()
    for k in pidList.keys():
        while ppid == 1 and os.path.exists('/proc/' + str(k)):
            os.kill(k, signal.SIGTERM)
            print "[stop] [%d] pid %d %s" % (os.getpid(), k, pidList[k])
            time.sleep(0.1)
    if ppid == 1:
        sys.exit(0)
    else:
        os._exit(0)

def subprocess_check(confArr, pidList):
    # check if children process down
    for k in pidList.keys():
        if not os.path.exists('/proc/' + str(k)):
            print "[down] pid %d %s" % (k, pidList[k])
            childPid = logmq(pidList[k][0], pidList[k][1], pidList[k][2])
            pidList.pop(k)
            if childPid:
                print "[start] pid %d %s" % (childPid, pidList[childPid])
    

class MyDaemon(Daemon):
    """
    rewrite function run for our biz
    """
    def run(self):
        # deal with signal
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, term)
        signal.signal(signal.SIGHUP, reload)

        confArr = conf_parser(conFile)

        for conf in confArr:
            childPid = logmq(conf[0], conf[1], conf[2])
            if childPid:
                print "[start] pid %d %s" % (childPid, pidList[childPid])

        while True and not stopTag:
            subprocess_check(confArr, pidList)
            time.sleep(1)

 
if __name__ == "__main__":
    """
    main function
    """
    parser = argparse.ArgumentParser("Log mq")
    parser.add_argument('-c' , '--config', help="config file, default " + conFile)
    parser.add_argument('-k' , '--action', help="action, start|stop|reload|restart", required=True)
    args = parser.parse_args()

    daemon = MyDaemon(pidfile=pidFile, stdout=logFile, stderr=logFile)
    #daemon = MyDaemon(pidfile=pidFile)

    if 'start' == args.action:
        daemon.start()
    elif 'stop' == args.action:
        daemon.stop()
    elif 'reload' == args.action:
        daemon.reload()
    elif 'restart' == args.action:
        daemon.restart()
    else:
        print "Unknown action"
        sys.exit(2)
    sys.exit(0)
