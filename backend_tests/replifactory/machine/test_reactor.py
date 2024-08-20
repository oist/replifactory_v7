from replifactory.machine import Reactor, reactor_command


class MockReactor(Reactor):
    @reactor_command
    def a(self):
        return True

    @reactor_command
    def b(self, arg1, arg2):
        return 0

    @reactor_command
    def c(self, arg1, arg2, arg3):
        return None


class MockReactorChild(MockReactor):
    @reactor_command
    def d(self, *args, **kwargs):
        return "d"


def test_reactor_ls_cmd():
    test_reactor = MockReactorChild()

    assert test_reactor.ls_cmd() == {
        "a": [],
        "b": ["arg1", "arg2"],
        "c": ["arg1", "arg2", "arg3"],
        "d": [],
    }


def test_reactor_cmd():
    test_reactor = MockReactorChild()

    assert test_reactor.cmd("a") is True
    assert test_reactor.cmd("b", 1, 2) == 0
    assert test_reactor.cmd("c", "1", 2, "three") is None
    assert test_reactor.cmd("d") == "d"


def test_reactor_cmd_raises():
    test_reactor = MockReactorChild()

    try:
        test_reactor.cmd("e")
    except AttributeError as exc:
        assert str(exc) == "No command named e found"
    else:
        assert False, "Expected AttributeError to be raised"
