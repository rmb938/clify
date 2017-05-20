import abc
import argparse
import signal
import threading

from clify.command import Command


class Daemon(Command):

    __metaclass__ = abc.ABCMeta

    def __init__(self, command: str, help: str):
        super().__init__(command, help)

    def start(self, args: argparse.Namespace) -> int:
        self.logger.info("Starting %s Daemon" % self.command)

        signal.signal(signal.SIGINT, self.on_shutdown)
        signal.signal(signal.SIGTERM, self.on_shutdown)
        signal.signal(signal.SIGABRT, self.on_shutdown)

        exit_code = self.run(args)
        if exit_code != 0:
            self.stop()

        while True:
            threads = threading.enumerate()
            if len(threads) <= 1:
                break
            for t in list(threads):
                if t != threading.currentThread():
                    t.join(1)

        self.logger.info("Stopped %s Daemon " % self.command)
        return exit_code

    @abc.abstractmethod
    def on_shutdown(self, signum=None, frame=None):
        pass

    def stop(self):
        self.on_shutdown()
