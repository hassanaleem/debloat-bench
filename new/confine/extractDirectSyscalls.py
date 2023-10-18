import os, sys, subprocess, signal
import logging
import optparse

sys.path.insert(0, './python-utils/')

import util

def isValidOpts(opts):
    """
    Check if the required options are sane to be accepted
        - Check if the provided files exist
        - Check if two sections (additional data) exist
        - Read all target libraries to be debloated from the provided list
    :param opts:
    :return:
    """
    if not options.outputpath:
        parser.error("Option -o should be provided.")
        return False

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

    parser.add_option("-o", "--outputpath", dest="outputpath", default=None, nargs=1,
                      help="Output folder path")

    parser.add_option("-d", "--debug", dest="debug", action="store_true", default=False,
                      help="Debug enabled/disabled")

    (options, args) = parser.parse_args()
    if isValidOpts(options):
        rootLogger = setLogPath("directsyscallextractor.log")

#        exceptList = ["lib", "grep", "sed", "bash", "sh", "touch", "mkdir", "systemctl-systemd", "chmod", "sv", "ssh-keygen", "sysctl", "env", "svlogd", "sleep", "mount", "blkid", "stat", "cat", "systemd-path", "dpkg-query", "df", "readlink", "rm", "cp", "systemd-sysctl", "hostnamectl", "loginctl", "uname", "id", "which", "dumb-init", "find", "basename", "awk", "hostname", "modprobe", "chown", "sort", "ip", "ldconfig", "egrep", "ldconfig.real", "mv", "dirname", "whoami", "date"]
        exceptList = []
        lib = ".so"


        for folderName in os.listdir(options.outputpath):
            fileList = list()
            removeList = list()
#            rootLogger.info("////////////Checking image: %s//////////////////", folderName)
            folderName = os.path.join(options.outputpath, folderName)
            if ( os.path.isdir(folderName) ):
                for fileName in os.listdir(folderName):
                    if ( util.isElf(folderName + "/" + fileName) ):
                        fileList.append(folderName + "/" + fileName)
                        for exceptItem in exceptList:
                            #if ( lib in fileName or fileName.startswith(exceptItem) or util.isGo(folderName + "/" + fileName, rootLogger) ):
                            if ( fileName.startswith(exceptItem) or util.isGo(folderName + "/" + fileName, rootLogger) ):
                                removeList.append(folderName + "/" + fileName)
                                break
            finalSet = set(fileList) - set(removeList)
#            rootLogger.info("List of binaries for %s: %s", folderName, str(finalSet))
            for filePath in finalSet:
                #rootLogger.debug("extraction direct syscall for %s", filePath)
                temp1 = util.extractDirectSyscalls(filePath, rootLogger)
                temp2 = util.extractLibcSyscalls(filePath, rootLogger)
                if ( temp1 != 0 or temp2 != 0 ):
                    rootLogger.info("filePath: %s is libcSyscall: %d directSyscall: %d", filePath, temp2, temp1)


