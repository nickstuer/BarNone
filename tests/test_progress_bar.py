import io
import re
import time

import pytest

from barnone import ProgressBar


def test_progress_bar_basic_update_and_done(capsys):
    pb = ProgressBar(total=5, width=10)
    for _ in range(5):
        pb.update()

    output, _ = capsys.readouterr()
    last_line = output.strip().splitlines()[-1]
    assert "100%" in last_line
    assert "5/5" in last_line


def test_progress_bar_basic_update_partial(capsys):
    pb = ProgressBar(total=5, width=10)
    for _ in range(4):
        pb.update()

    output, _ = capsys.readouterr()
    last_line = output.strip().splitlines()[-1]
    assert "80%" in last_line
    assert "4/5" in last_line


def test_progress_bar_prefix_suffix(capsys):
    pb = ProgressBar(total=3, prefix="Start", suffix="End")
    pb.update()
    pb.finish()
    output, _ = capsys.readouterr()
    last_line = output.strip().splitlines()[-1]
    assert "Start" in last_line
    assert "End" in last_line


def test_progress_bar_eta_true(capsys):
    pb = ProgressBar(total=2)
    pb.update()
    output, _ = capsys.readouterr()
    last_line = output.strip().splitlines()[-1]
    assert "ETA" in last_line


def test_progress_bar_color_false(capsys):
    pb = ProgressBar(total=10)
    for _ in range(10):
        pb.update()
    output, _ = capsys.readouterr()
    assert "\033[38;2;" not in output
    assert "\033[0m" not in output


def test_progress_bar_multiple_steps(capsys):
    pb = ProgressBar(total=10, width=10)
    pb.update(3)
    pb.update(2)
    pb.update(5)
    output, _ = capsys.readouterr()
    assert "10/10" in output
    assert "100%" in output


def test_progress_bar_eta_time_hours(capsys):
    pb = ProgressBar(total=500000)
    pb._start_time = time.time() - 0.01
    pb.update()

    output, _ = capsys.readouterr()
    last_line = output.strip().splitlines()[-1]
    assert "ETA" in last_line
    assert re.search(r"\b\d+h \d+m \d+s\b", last_line)


def test_progress_bar_eta_time_mins(capsys):
    pb = ProgressBar(total=20000)
    pb._start_time = time.time() - 0.01
    pb.update()

    output, _ = capsys.readouterr()
    last_line = output.strip().splitlines()[-1]
    print(last_line)
    assert "ETA" in last_line
    assert re.search(r"\b\d+m \d+s\b", last_line)
    assert "h" not in last_line


def test_progress_bar_eta_time_secs(capsys):
    pb = ProgressBar(total=5000)
    pb._start_time = time.time() - 0.01
    pb.update()

    output, _ = capsys.readouterr()
    last_line = output.strip().splitlines()[-1]
    assert "ETA" in last_line
    assert re.search(r"\b\d+s\b", last_line)
    assert "h" not in last_line
    assert "m" not in last_line


def test_progress_bar_eta_time_less_than_ten_secs(capsys):
    pb = ProgressBar(total=40)
    pb._start_time = time.time() - 0.01
    pb.update()

    output, _ = capsys.readouterr()
    last_line = output.strip().splitlines()[-1]
    assert "ETA" in last_line
    assert re.search(r"\b\d+\.\d{1}s\b", last_line)


def test_progress_bar_overrun(capsys):
    pb = ProgressBar(total=5, width=10)
    pb.update(5)
    pb.update(1)
    output, _ = capsys.readouterr()
    last_line = output.strip().splitlines()[-1]
    assert "Warning: Progress bar overrun." in last_line
    assert "Current Step: 6 of 5." in last_line


def test_start_after_started(capsys):
    pb = ProgressBar(total=5)

    with pytest.raises(RuntimeError, match="Progress bar has already been started."):
        pb.start()


def test_update_before_start(capsys):
    pb = ProgressBar(total=5, auto_start=False)

    with pytest.raises(RuntimeError, match="Progress bar has not been started yet."):
        pb.update()


def test_finish_early_shows_complete(capsys):
    pb = ProgressBar(total=5)
    pb.update(3)
    pb.finish()

    output, _ = capsys.readouterr()
    last_line = output.strip().splitlines()[-1]
    assert "100%" in last_line
    assert "5/5" in last_line
    assert "ETA 0.0s" in last_line


def test_write_basic_message_sets_last_line_len_and_writes(monkeypatch):
    pb = ProgressBar(total=1)
    stream = io.StringIO()
    pb._stream = stream
    pb._last_line_len = 0

    pb._write("Hello World", pad_line=True, flush=True)
    assert stream.getvalue() == "Hello World"
    assert pb._last_line_len == len("Hello World")


def test_write_message_pads_to_last_line_len(monkeypatch):
    pb = ProgressBar(total=1)
    stream = io.StringIO()
    pb._stream = stream
    pb._last_line_len = 15

    pb._write("Short", pad_line=False, flush=True)
    # Should pad to 15 chars
    assert stream.getvalue() == "Short" + " " * (15 - len("Short"))
    # Should not update _last_line_len
    assert pb._last_line_len == 15


def test_write_message_updates_last_line_len_when_pad_line_true(monkeypatch):
    pb = ProgressBar(total=1)
    stream = io.StringIO()
    pb._stream = stream
    pb._last_line_len = 5

    pb._write("Longer message", pad_line=True, flush=True)
    assert pb._last_line_len == len("Longer message")


def test_write_flush_false(monkeypatch):
    pb = ProgressBar(total=1)
    stream = io.StringIO()
    pb._stream = stream
    pb._last_line_len = 0

    # Monkeypatch flush to track calls
    called = {}

    def fake_flush():
        called["flushed"] = True

    pb._stream.flush = fake_flush

    pb._write("Test", pad_line=True, flush=False)
    assert called.get("flushed") is None  # flush should not be called


def test_write_flush_true(monkeypatch):
    pb = ProgressBar(total=1)
    stream = io.StringIO()
    pb._stream = stream
    pb._last_line_len = 0

    called = {}

    def fake_flush():
        called["flushed"] = True

    pb._stream.flush = fake_flush

    pb._write("Test", pad_line=True, flush=True)
    assert called.get("flushed") is True
