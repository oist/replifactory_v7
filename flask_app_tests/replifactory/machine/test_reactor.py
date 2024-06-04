from flask_app.replifactory.machine import Reactor


class TestReactor(Reactor):
    def cmd_a(self):
        return True

    def cmd_b(self, arg1, arg2):
        return 0

    def cmd_c(self, arg1, arg2, arg3):
        return None


class TestReactorChild(TestReactor):
    def cmd_d(self):
        return 'd'


def test_reactor_ls_cmd():
    test_reactor = TestReactorChild()

    assert test_reactor.ls_cmd() == ['cmd_a', 'cmd_b', 'cmd_c', 'cmd_d']


def test_reactor_cmd():
    test_reactor = TestReactorChild()

    assert test_reactor.cmd('a') is True
    assert test_reactor.cmd('b', 1, 2) == 0
    assert test_reactor.cmd('c', "1", 2, "three") is None
    assert test_reactor.cmd('d') == 'd'


def test_reactor_cmd_raises():
    test_reactor = TestReactorChild()

    try:
        test_reactor.cmd('e')
    except AttributeError as exc:
        assert str(exc) == "No command named e found"
    else:
        assert False, "Expected AttributeError to be raised"
