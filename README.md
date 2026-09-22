# 🔐 Password Generator

[![tests](https://github.com/VINAY-G-007/password-generator/actions/workflows/tests.yml/badge.svg)](https://github.com/VINAY-G-007/password-generator/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

A small, dependency-free command-line tool that generates **strong, truly random passwords**
with Python's cryptographically secure [`secrets`](https://docs.python.org/3/library/secrets.html) module.

Use it **interactively** (it asks you a few questions) or in **one line with flags**, which is handy for scripts.

---

## ✨ Features

- **Secure randomness:** uses `secrets`, not `random` (whose output can be predicted).
- **Every chosen character type is guaranteed:** ask for digits and you *will* get at least one digit.
- **You choose what goes in:** uppercase, lowercase, digits and symbols, each on or off.
- **No look-alikes (optional):** leave out `I l 1 | O 0 o` for passwords you have to read out or type.
- **Strength meter:** an estimate in bits of entropy (Weak / Fair / Strong / Very strong).
- **Two modes:** friendly prompts, or flags for scripting (`-l 20 -n 5`).
- **Never crashes on bad input:** wrong answers are simply asked again.
- **Zero dependencies**, with 35 automated tests run on Linux and Windows by GitHub Actions.

## 🚀 Quick start

You only need **Python 3.9 or newer**. Nothing to install.

```bash
git clone https://github.com/VINAY-G-007/password-generator.git
cd password-generator
python password_gen.py
```

## 🖥️ Usage

### Interactive mode

Run it with no options and answer the questions. Press **Enter** to accept the default shown in brackets.

```text
> python password_gen.py
=== Password Generator ===
Press Enter to accept the default shown in [brackets].

Password length [16]: 20
Include uppercase letters (A-Z)? [Y/n]:
Include lowercase letters (a-z)? [Y/n]:
Include digits (0-9)? [Y/n]:
Include symbols (!@#$...)? [Y/n]: n
Leave out look-alike characters (I l 1 | O 0 o)? [y/N]: y
How many passwords [1]: 3

Your passwords:
  1. P3uLVDd88WqV7aDcGjX9
  2. 29fkYMMZcG2bK9YzVU7W
  3. fZvQpeVe63NbHENc2fvA
Strength: Very strong (~116 bits of entropy)
```

### Command-line mode

| Option | What it does | Default |
|---|---|---|
| `-l`, `--length N` | Password length (4 to 128) | `16` |
| `-n`, `--count N` | How many passwords to make (1 to 50) | `1` |
| `--no-upper` | Leave out uppercase letters | off |
| `--no-lower` | Leave out lowercase letters | off |
| `--no-digits` | Leave out digits | off |
| `--no-symbols` | Leave out symbols | off |
| `--exclude-ambiguous` | Leave out look-alike characters `I l 1 \| O 0 o` | off |
| `-h`, `--help` | Show all options | |

```bash
python password_gen.py -l 24                                    # one 24-character password
python password_gen.py -l 12 -n 3 --no-symbols                  # three passwords, letters and digits only
python password_gen.py -l 6 --no-upper --no-lower --no-symbols  # a 6-digit PIN
python password_gen.py -l 20 | clip                             # Windows: copy it straight to the clipboard
```

```text
> python password_gen.py -l 12 -n 3 --no-symbols
3NYVcHVIGej0
HfBt6YLPh1Su
MBjrgd8liVPF
Strength: Strong (~71 bits of entropy)
```

The passwords go to standard output and the strength line goes to standard error,
so piping (`| clip`, `> passwords.txt`) captures only the passwords.

### Install it as a command (optional)

```bash
pip install .
passgen -l 20
```

## 🧠 How it works

1. Build the pool from the character types you picked (optionally removing look-alike characters).
2. Pick **one character from each selected type**, so none can be missing.
3. Fill the remaining positions from the whole pool with `secrets.choice`.
4. **Shuffle** with `secrets.SystemRandom().shuffle`, so the guaranteed characters are not always at the start.

Step 2 matters more than it looks: if every character is drawn from one combined pool,
about **half of all 8-character passwords** end up missing at least one of the four selected types.

**Strength** is estimated as `entropy = length × log2(pool size)` bits:

| Bits of entropy | Label |
|---|---|
| under 40 | Weak |
| 40 to 59 | Fair |
| 60 to 79 | Strong |
| 80 and above | Very strong |

For example, 16 characters drawn from all 94 printable characters give about 16 × 6.55 ≈ **105 bits** (Very strong),
while a 6-digit PIN gives only about **20 bits** (Weak).

> **Why not `random`?** The `random` module is built for simulations and games. It is fast but predictable:
> after seeing enough output, the next values can be worked out. `secrets` uses the operating system's secure
> random source, which is the right tool for passwords, tokens and keys.

## 🧪 Running the tests

```bash
pip install -r requirements-dev.txt
pytest
```

The 35 tests cover length limits, the character-type guarantee, excluded types, look-alike removal,
randomness, the strength meter, every command-line option, and the interactive prompts (including bad
answers and Ctrl+C). GitHub Actions runs them on every push: Python 3.10, 3.12 and 3.13 on Linux, and
Python 3.12 on Windows.

## 📁 Project structure

```text
password-generator/
├── password_gen.py            # generator, strength meter, interactive and command-line modes
├── tests/
│   └── test_password_gen.py   # pytest suite (35 tests)
├── .github/workflows/
│   └── tests.yml              # CI: runs the tests on Linux and Windows
├── pyproject.toml             # package info (pip install . gives the `passgen` command) + pytest settings
├── requirements-dev.txt       # test dependency (pytest)
├── LICENSE
└── README.md
```

## 🗺️ Ideas for next steps

- Copy the password to the clipboard automatically
- Passphrase mode, e.g. `river-candle-orbit-velvet`
- A small desktop window with Tkinter

## 📄 License

[MIT](LICENSE) © 2026 Vinay G Jampannanavar
