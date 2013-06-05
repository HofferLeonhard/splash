import sys, optparse, resource

# A global reference must be kept to QApplication, otherwise the process will
# segfault
qtapp = None

def install_qtreactor():
    global qtapp

    from PyQt4.QtGui import QApplication
    qtapp = QApplication(sys.argv)
    import qt4reactor
    qt4reactor.install()

def parse_opts():
    op = optparse.OptionParser()
    op.add_option("-f", "--logfile", help="log file")
    op.add_option("-p", "--port", type="int", default=8050,
        help="port to listen to (default: %default)")
    return op.parse_args()

def start_logging(opts):
    from twisted.python import log
    from twisted.python.logfile import DailyLogFile
    if opts.logfile:
        logfile = DailyLogFile.fromFullPath(opts.logfile)
    else:
        logfile = sys.stderr
    log.startLogging(logfile)
    log.msg("Open files limit: %d" % resource.getrlimit(resource.RLIMIT_NOFILE)[0])

def splash_started(opts, stderr):
    if opts.logfile:
        stderr.write("Splash started - logging to: %s\n" % opts.logfile)

def bump_nofile_limit():
    _, n = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (n, n))

def main():
    install_qtreactor()

    from twisted.web.server import Site
    from twisted.internet import reactor
    from splash.resources import Root

    opts, _ = parse_opts()

    bump_nofile_limit()
    reactor.callWhenRunning(splash_started, opts, sys.stderr)
    start_logging(opts)
    root = Root()
    factory = Site(root)
    reactor.listenTCP(opts.port, factory)
    reactor.run()

if __name__ == "__main__":
    main()