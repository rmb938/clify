from clify.app import Application
from clify.command import Command
from clify.daemon import Daemon


class MyApp(Application):
    def __init__(self):
        super().__init__('myapp', '')

    @property
    def version(self) -> str:
        return '1.0.0'

    def logging_config(self, log_level: int) -> dict:
        return {
            'version': 1,
            'formatters': {
                'default': {
                    'format': '',
                    'datefmt': ''
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'default'
                }
            },
            'loggers': {
                self.__module__.split(".")[0]: {
                    'level': log_level,
                    'handlers': ['console']
                }
            }
        }


class FirstCommand(Command):

    def __init__(self):
        super().__init__('first', 'This is the first command')

    def setup_arguments(self, parser):
        parser.add_argument('-e', '--exitcode', help='set the exit code', type=int, default=0)

    def run(self, args) -> int:
        self.logger.info("This is the first command")
        self.logger.debug("This is a debug message")

        if args.exitcode != 0:
            self.logger.error("Exiting with non 0")

        return args.exitcode


class SecondCommand(Command):

    def __init__(self):
        super().__init__('second', 'This is the second command')

    def setup_arguments(self, parser):
        pass

    def setup(self, args) -> int:
        self.logger.error("We have failed the setup!")
        return 1

    def run(self, args) -> int:
        self.logger.info("This is the second command")

        return 0


class SubCommand(Command):

    def __init__(self):
        super().__init__('sub', 'This is a sub command')

    def setup_arguments(self, parser):
        pass

    def run(self, args) -> int:
        self.logger.info("We are running a sub command")

        return 0


class ParentCommand(Command):

    def __init__(self):
        super().__init__('parent', 'This is a parent command')

    def setup_arguments(self, parser):
        pass

    def add_subcommands(self):
        SubCommand().register_subcommand(self)

    def run(self, args) -> int:
        self.logger.info("These logs should not be seen")

        return 0


class DaemonCommand(Daemon):

    def __init__(self):
        super().__init__('daemon', 'This runs a daemon')

    def setup_arguments(self, parser):
        pass

    def on_shutdown(self, signum=None, frame=None):
        self.logger.info("We are shutting down")

    def run(self, args) -> int:
        self.logger.info("Running some long running task")

        return 0
