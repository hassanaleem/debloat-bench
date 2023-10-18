import os, sys, subprocess, signal
import logging
import optparse

import syscall
import seccomp

def isValidOpts(opts):
    """
    Check if the required options are sane to be accepted
        - Check if the provided files exist
        - Check if two sections (additional data) exist
        - Read all target libraries to be debloated from the provided list
    :param opts:
    :return:
    """
#    if not options.perfpath:
#        parser.error("All options -e, -p and -l and should be provided.")
#        return False

    return True


def setLogPath(logPath):
    """
    Set the property of the logger: path, config, and format
    :param logPath:
    :return:
    """
    if os.path.exists(logPath):
        os.remove(logPath)

    rootLogger = logging.getLogger("coverage")
    if options.debug:
        logging.basicConfig(filename=logPath, level=logging.DEBUG)
        rootLogger.setLevel(logging.DEBUG)
    else:
        logging.basicConfig(filename=logPath, level=logging.INFO)
        rootLogger.setLevel(logging.INFO)

#    ch = logging.StreamHandler(sys.stdout)
    consoleHandler = logging.StreamHandler()
    rootLogger.addHandler(consoleHandler)
    return rootLogger
#    rootLogger.addHandler(ch)

if __name__ == '__main__':
    """
    Main function for finding physical memory usage of process
    """
    usage = "Usage: %prog -e <Target executable path> -p <PID of process to retrieve information about>"

    parser = optparse.OptionParser(usage=usage, version="1")

    parser.add_option("-s", "--syscallpath", dest="syscallpath", default=None, nargs=1,
                      help="Perf output path")

    parser.add_option("-o", "--oldprofilepath", dest="oldprofilepath", default=None, nargs=1,
                      help="Old profile path")

    parser.add_option("-d", "--debug", dest="debug", action="store_true", default=False,
                      help="Debug enabled/disabled")

    (options, args) = parser.parse_args()
    if isValidOpts(options):
        rootLogger = setLogPath("syscall.log")
        syscallExtractor = syscall.Syscall(rootLogger)
        #auditdMap = syscallExtractor.createMapWithAuditd()
        syscallMap = syscallExtractor.createMap()

        exceptList = ["access","arch_prctl","brk","close","execve","exit_group","fcntl","fstat","geteuid","lseek","mmap","mprotect","munmap","openat","prlimit64","read","rt_sigaction","rt_sigprocmask","set_robust_list","set_tid_address","stat","statfs","write","setns","capget","capset","chdir","fchown","futex","getdents64","getpid","getppid","lstat","openat","prctl","setgid","setgroups","setuid","stat","io_setup","getdents","clone","readlinkat","newfstatat","getrandom","sigaltstack","getresgid","getresuid","setresgid","setresuid","alarm","getsid","getpgrp", "epoll_pwait", "vfork"]

        myFile = open(options.syscallpath, 'r')
        line = myFile.readline()
        syscallList = []
        blackList = []
        while ( line ):
            syscallList.append(int(line.strip()))
            line = myFile.readline()
        i = 0
        while i < 400:
            if ( i not in syscallList and syscallMap.get(i, None) and syscallMap[i] not in exceptList):
                blackList.append(syscallMap[i])
            i += 1

        seccompProfile = seccomp.Seccomp(rootLogger)
        if ( options.oldprofilepath ):
            blackListProfile = seccompProfile.createProfileWithOld(options.oldprofilepath, blackList)
        else:
            blackListProfile = seccompProfile.createProfile(blackList)
        outputPath = options.syscallpath[:options.syscallpath.index(".")] + ".seccomp.json"
        outputFile = open(outputPath, 'w')
        outputFile.write(blackListProfile)
        outputFile.flush()
        outputFile.close()

        #syscallExtractor.findDiff(auditdMap, oldMap)
