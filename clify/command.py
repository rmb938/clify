import abc
import argparse

import logging


class Command(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, command: str, help: str):
        self.command = command
        self.help = help

        self.logger = logging.getLogger("%s.%s" % (self.__module__, self.__class__.__name__))
        self.subcommands = []
        self.parent = None

    def register_subcommand(self, parent):
            self.parent = parent
            parent.subcommands.append(self)

    def register(self, app):
        app.register_command(self)

    @abc.abstractmethod
    def setup_arguments(self, parser):
        raise NotImplementedError

    def add_subcommands(self):
        pass

    def create_parser(self, subparsers):
        parser = subparsers.add_parser(self.command, help=self.help, description=self.help,
                                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        self.add_subcommands()

        if len(self.subcommands) > 0:
            subsubparsers = parser.add_subparsers()
            for subcommand in self.subcommands:
                subcommand.create_parser(subsubparsers)
        else:
            if self.parent is not None:
                self.parent.setup_arguments(parser)
            self.setup_arguments(parser)
            parser.set_defaults(func=self)

        return parser

    def setup(self, args) -> int:
        return 0

    @abc.abstractmethod
    def run(self, args) -> int:
        raise NotImplementedError
