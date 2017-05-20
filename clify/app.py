import abc
import argparse
import sys

import logging
import logging.config

from io import StringIO

from clify.command import Command
from clify.daemon import Daemon


class Application(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, name: str, help: str):
        self.name = name
        self.help = help

        self.logger = logging.getLogger("%s.%s" % (self.__module__, self.__class__.__name__))
        self.commands = []

    def register_command(self, command: Command):
        self.commands.append(command)

    def __handle_exception(self, exc_type, exc_value, exc_traceback):  # pragma: no cover
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        self.logger.error('Uncaught exception', exc_info=(exc_type, exc_value, exc_traceback))

    @abc.abstractmethod
    def logging_config(self, log_level: int) -> dict:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def version(self) -> str:
        raise NotImplementedError

    def _setup_logging(self, verbose_level: int):
        log_level = logging.INFO

        if verbose_level > 0:
            log_level = logging.DEBUG

        logging.config.dictConfig(self.logging_config(log_level))
        sys.excepthook = self.__handle_exception

    def __create_parser(self, add_help: bool=True, commands: bool=True) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(prog=self.name, formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                         add_help=add_help)
        parser.add_argument('-v', '--verbose', help='Print verbose statements', action='count', default=0)
        parser.add_argument('--version', help='Show the version of %s' % self.name, action='version',
                            version='Version: %s ' % self.version)

        if commands:
            subparsers = parser.add_subparsers()
            for command in self.commands:
                command.create_parser(subparsers)

        return parser

    def _execute_command(self, parser: argparse.ArgumentParser, test: bool=False, args: dict=None) -> int:
        args = parser.parse_args(args)
        command = args.func

        if test and isinstance(command, Daemon):
            raise TypeError("Cannot test Daemon commands due to the possibility of being long running!")

        setup_exit_code = command.setup(args)
        if setup_exit_code != 0:
            return setup_exit_code

        if isinstance(command, Daemon):
            return command.start(args)

        return command.run(args)

    def test_command(self, args: dict) -> (int, str):
        log_stream = StringIO()
        log_handler = logging.StreamHandler(log_stream)
        module_logger = logging.getLogger(self.__module__.split(".")[0])
        module_logger.addHandler(log_handler)

        def remove_handler():
            module_logger.removeHandler(log_handler)

        parser = self.__create_parser()

        try:
            exit_code = self._execute_command(parser, True, args)
        except Exception as e:  # pragma: no cover
            module_logger.exception(e)
            exit_code = -1

        log_handler.flush()
        logs = log_stream.getvalue()
        remove_handler()

        return exit_code, logs

    def run(self):  # pragma: no cover

        # Parse Verbose to setup logging
        parser = self.__create_parser(add_help=False, commands=False)
        args = parser.parse_known_args()[0]
        self._setup_logging(args.verbose)

        # Parse all commands
        parser = self.__create_parser()

        if len(sys.argv) == 1:
            parser.print_help()
            parser.exit(1)

        sys.exit(self._execute_command(parser))
