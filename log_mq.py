#!/usr/bin/env python
 
import os, sys, time, signal, re, argparse
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
    parser = argparse.ArgumentParser("Log mq")
    parser.add_argument('-c' , '--config', help="config file, default " + conFile)
    parser.add_argument('-k' , '--action', help="action, start|stop|restart", required=True)
    args = parser.parse_args()

    #daemon = MyDaemon(pidfile=pidFile, stdout=logFile, stderr=logFile)
    daemon = MyDaemon(pidfile=pidFile)

    if 'start' == args.action:
        daemon.start()
    elif 'stop' == args.action:
        daemon.stop()
    elif 'restart' == args.action:
        daemon.restart()
    else:
        print "Unknown action"
        sys.exit(2)
    sys.exit(0)
