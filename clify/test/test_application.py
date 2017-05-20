import pytest

from clify.test.base import MyApp, FirstCommand, DaemonCommand, SecondCommand, ParentCommand


class TestApplication(object):

    @pytest.fixture()
    def application(self):
        app = MyApp()
        app._setup_logging(1)
        FirstCommand().register(app)
        SecondCommand().register(app)
        ParentCommand().register(app)
        DaemonCommand().register(app)
        return app

    def test_command(self, application):
        exit_code, logs = application.test_command(['first'])
        assert exit_code == 0
        assert 'This is the first command' in logs
        assert 'This is a debug message' in logs

    def test_exit_code(self, application):
        exit_code, logs = application.test_command(['first', '-e', '1'])
        assert exit_code == 1
        assert 'Exiting with non 0' in logs

    def test_setup_failure(self, application):
        exit_code, logs = application.test_command(['second'])
        assert exit_code == 1
        assert 'We have failed the setup!' in logs

    def test_subcommand(self, application):
        exit_code, logs = application.test_command(['parent', 'sub'])
        assert exit_code == 0
        assert 'These logs should not be seen' not in logs
        assert 'We are running a sub command' in logs

    def test_daemon(self, application):
        exit_code, logs = application.test_command(['daemon'])
        assert exit_code == -1
        assert 'Cannot test Daemon commands due to the possibility of being long running!' in logs
