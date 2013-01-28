#!/usr/bin/env python
 
import os, sys, time, signal, re
from daemon import Daemon

logFile = '/var/log/logmq.log'
pidFile = '/var/run/logmq.pid'
pidList = {}
conFile = '/etc/logmq.conf'

def logmq(ip, port, logfile):
    """
    start access_log zmq bind
    """
    pid = os.fork()
    if pid != 0:
        pidList[pid] = [ip, port, logfile];
    else:
        while True:
            if os.getppid() == 1:
                os._exit(0)
            time.sleep(1)


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

class MyDaemon(Daemon):
    """
    rewrite function run for our biz
    """
    def run(self):
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)

        confArr = conf_parser(conFile)
        print confArr

        for conf in confArr:
            logmq(conf[0], conf[1], conf[2])

        print pidList

        while True:
            downpid = pidList[os.wait()[0]]
            logmq(downpid[0], downpid[1], downpid[2])
            time.sleep(1)

 
if __name__ == "__main__":
    """
    main function
    """
    

    #daemon = MyDaemon(pidfile=pidFile, stdout=logFile, stderr=logFile)
    daemon = MyDaemon(pidfile=pidFile)

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
