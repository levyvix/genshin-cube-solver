from genshin_cube_solver.utils import _write_console


class AsciiStream:
    encoding = "ascii"

    def __init__(self):
        self.value = ""

    def write(self, value):
        value.encode(self.encoding)
        self.value += value


def test_console_sink_escapes_characters_unavailable_in_windows_code_page():
    stream = AsciiStream()

    _write_console("solution → found", stream)

    assert stream.value == r"solution \u2192 found"
