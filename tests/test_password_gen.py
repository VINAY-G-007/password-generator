"""Tests for password_gen.py.  Run from the project folder with:  pytest"""

import string

import pytest

import password_gen as pg


# ---------------------------------------------------------------------------
# generate_password
# ---------------------------------------------------------------------------

def test_default_password_has_default_length():
    assert len(pg.generate_password()) == pg.DEFAULT_LENGTH


@pytest.mark.parametrize("length", [pg.MIN_LENGTH, 8, 32, pg.MAX_LENGTH])
def test_custom_lengths(length):
    assert len(pg.generate_password(length)) == length


def test_every_selected_type_is_always_present():
    # 4 characters and 4 types: each type has to appear exactly once.
    for _ in range(300):
        password = pg.generate_password(4)
        assert any(c in string.ascii_uppercase for c in password)
        assert any(c in string.ascii_lowercase for c in password)
        assert any(c in string.digits for c in password)
        assert any(c in string.punctuation for c in password)


def test_unselected_types_never_appear():
    allowed = string.ascii_lowercase + string.digits
    for _ in range(100):
        password = pg.generate_password(20, upper=False, symbols=False)
        assert all(c in allowed for c in password)


def test_digits_only_pin():
    pin = pg.generate_password(6, upper=False, lower=False, symbols=False)
    assert pin.isdigit()
    assert len(pin) == 6


def test_exclude_ambiguous_characters():
    for _ in range(100):
        password = pg.generate_password(64, exclude_ambiguous=True)
        assert not set(password) & set(pg.AMBIGUOUS)


def test_passwords_are_random():
    passwords = {pg.generate_password(16) for _ in range(200)}
    assert len(passwords) == 200


def test_no_character_type_selected_raises():
    with pytest.raises(ValueError, match="at least one"):
        pg.generate_password(12, upper=False, lower=False, digits=False, symbols=False)


@pytest.mark.parametrize("length", [0, -5, pg.MIN_LENGTH - 1, pg.MAX_LENGTH + 1])
def test_length_out_of_range_raises(length):
    with pytest.raises(ValueError, match="between"):
        pg.generate_password(length)


@pytest.mark.parametrize("length", ["12", 12.5, None, True])
def test_length_must_be_a_whole_number(length):
    with pytest.raises(TypeError):
        pg.generate_password(length)


# ---------------------------------------------------------------------------
# Strength estimate
# ---------------------------------------------------------------------------

def test_entropy_bits():
    assert pg.entropy_bits(10, 2) == 10  # 10 coin flips = 10 bits
    assert pg.entropy_bits(0, 94) == 0
    assert pg.entropy_bits(8, 1) == 0


@pytest.mark.parametrize("bits, label", [
    (20, "Weak"), (45, "Fair"), (70, "Strong"), (100, "Very strong"),
])
def test_strength_labels(bits, label):
    assert pg.strength_label(bits) == label


def test_describe_strength():
    pin = pg.describe_strength(4, upper=False, lower=False, symbols=False)
    assert pin.startswith("Strength: Weak")
    strong = pg.describe_strength(16)
    assert strong.startswith("Strength: Very strong")


# ---------------------------------------------------------------------------
# Command-line mode
# ---------------------------------------------------------------------------

def test_cli_prints_requested_passwords(capsys):
    assert pg.main(["--length", "20", "--count", "3"]) == 0
    out, err = capsys.readouterr()
    lines = out.splitlines()
    assert len(lines) == 3
    assert all(len(line) == 20 for line in lines)
    assert "Strength:" in err


def test_cli_no_symbols(capsys):
    pg.main(["-l", "50", "--no-symbols"])
    password = capsys.readouterr().out.strip()
    assert password.isalnum()


@pytest.mark.parametrize("args", [
    ["--no-upper", "--no-lower", "--no-digits", "--no-symbols"],
    ["--length", "2"],
    ["--length", "abc"],
    ["--count", "0"],
])
def test_cli_rejects_bad_options(args):
    with pytest.raises(SystemExit) as exc:
        pg.main(args)
    assert exc.value.code == 2


# ---------------------------------------------------------------------------
# Interactive mode
# ---------------------------------------------------------------------------

def feed(monkeypatch, answers):
    """Make input() return the given answers one by one."""
    replies = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(replies))


def passwords_in(output):
    lines = [line.strip() for line in output.splitlines()]
    return [line.split(". ", 1)[1] for line in lines if line[:1].isdigit() and ". " in line]


def test_interactive_accepts_defaults(monkeypatch, capsys):
    feed(monkeypatch, [""] * 7)  # press Enter at every question
    assert pg.main([]) == 0
    passwords = passwords_in(capsys.readouterr().out)
    assert len(passwords) == 1
    assert len(passwords[0]) == pg.DEFAULT_LENGTH


def test_interactive_reprompts_on_bad_input(monkeypatch, capsys):
    feed(monkeypatch, [
        "abc", "2", "10",              # length: not a number, too short, then 10
        "maybe", "n", "n", "y", "n",   # upper: bad answer then no; lower no; digits yes; symbols no
        "", "2",                       # keep look-alikes, make two passwords
    ])
    assert pg.main([]) == 0
    out = capsys.readouterr().out
    assert "whole number" in out
    assert "from 4 to 128" in out
    assert "Please type y or n" in out
    passwords = passwords_in(out)
    assert len(passwords) == 2
    assert all(p.isdigit() and len(p) == 10 for p in passwords)


def test_interactive_needs_a_character_type(monkeypatch, capsys):
    feed(monkeypatch, ["8", "n", "n", "n", "n", "y", "n", "n", "n", "", ""])
    assert pg.main([]) == 0
    out = capsys.readouterr().out
    assert "at least one character type" in out
    assert passwords_in(out)[0].isupper()


def test_interactive_ctrl_c_is_handled(monkeypatch, capsys):
    def interrupt(prompt=""):
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", interrupt)
    assert pg.main([]) == 1
    assert "Cancelled" in capsys.readouterr().out
