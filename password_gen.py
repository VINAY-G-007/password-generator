"""Password Generator - create strong, random passwords from the command line.

It uses Python's built-in ``secrets`` module, which is made for security.
(The ``random`` module is NOT safe for passwords: its output can be predicted.)

Usage:
    python password_gen.py                          # interactive mode, asks you questions
    python password_gen.py --length 20              # one 20-character password
    python password_gen.py -l 12 -n 5 --no-symbols  # five 12-character passwords, no symbols
    python password_gen.py --help                   # every option
"""

import argparse
import math
import secrets
import string
import sys

UPPERCASE = string.ascii_uppercase   # A-Z
LOWERCASE = string.ascii_lowercase   # a-z
DIGITS = string.digits               # 0-9
SYMBOLS = string.punctuation         # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
AMBIGUOUS = "Il1|O0o"                # characters that look alike in many fonts

MIN_LENGTH = 4
MAX_LENGTH = 128
DEFAULT_LENGTH = 16
MAX_COUNT = 50


def character_groups(upper=True, lower=True, digits=True, symbols=True,
                     exclude_ambiguous=False):
    """Return the character groups the user chose, as a list of strings."""
    choices = [(upper, UPPERCASE), (lower, LOWERCASE), (digits, DIGITS), (symbols, SYMBOLS)]
    groups = [chars for wanted, chars in choices if wanted]
    if exclude_ambiguous:
        groups = ["".join(c for c in chars if c not in AMBIGUOUS) for chars in groups]
    return groups


def generate_password(length=DEFAULT_LENGTH, upper=True, lower=True, digits=True,
                      symbols=True, exclude_ambiguous=False):
    """Return one random password.

    Every character type you select is guaranteed to appear at least once.
    (Picking every character from one combined pool, the simple approach,
    leaves out a selected type in about half of all 8-character passwords.)
    """
    if isinstance(length, bool) or not isinstance(length, int):
        raise TypeError("length must be a whole number")
    if not MIN_LENGTH <= length <= MAX_LENGTH:
        raise ValueError(f"length must be between {MIN_LENGTH} and {MAX_LENGTH}")

    groups = character_groups(upper, lower, digits, symbols, exclude_ambiguous)
    if not groups:
        raise ValueError("select at least one character type")

    # 1) one guaranteed character from each selected group
    chars = [secrets.choice(group) for group in groups]
    # 2) fill the remaining positions from all selected characters
    pool = "".join(groups)
    chars += [secrets.choice(pool) for _ in range(length - len(chars))]
    # 3) shuffle, so the guaranteed characters are not always at the start
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def entropy_bits(length, pool_size):
    """Estimate strength in bits of entropy: length x log2(pool size)."""
    if length <= 0 or pool_size <= 1:
        return 0.0
    return length * math.log2(pool_size)


def strength_label(bits):
    """Turn bits of entropy into a friendly label."""
    if bits < 40:
        return "Weak"
    if bits < 60:
        return "Fair"
    if bits < 80:
        return "Strong"
    return "Very strong"


def describe_strength(length, **options):
    """One-line summary, e.g. 'Strength: Very strong (~105 bits of entropy)'."""
    pool_size = len("".join(character_groups(**options)))
    bits = entropy_bits(length, pool_size)
    return f"Strength: {strength_label(bits)} (~{bits:.0f} bits of entropy)"


# ---------------------------------------------------------------------------
# Interactive mode
# ---------------------------------------------------------------------------

def ask_yes_no(question, default=True):
    """Ask a yes/no question. Pressing Enter picks the default."""
    hint = "Y/n" if default else "y/N"
    while True:
        answer = input(f"{question} [{hint}]: ").strip().lower()
        if answer == "":
            return default
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  Please type y or n.")


def ask_number(question, default, minimum, maximum):
    """Ask for a whole number in a range. Pressing Enter picks the default."""
    while True:
        answer = input(f"{question} [{default}]: ").strip()
        if answer == "":
            return default
        try:
            number = int(answer)
        except ValueError:
            print("  Please enter a whole number, e.g. 16.")
            continue
        if minimum <= number <= maximum:
            return number
        print(f"  Please enter a number from {minimum} to {maximum}.")


def interactive():
    """Ask for the user's preferences, then print the password(s)."""
    print("=== Password Generator ===")
    print("Press Enter to accept the default shown in [brackets].\n")

    length = ask_number("Password length", DEFAULT_LENGTH, MIN_LENGTH, MAX_LENGTH)
    while True:
        options = {
            "upper": ask_yes_no("Include uppercase letters (A-Z)?"),
            "lower": ask_yes_no("Include lowercase letters (a-z)?"),
            "digits": ask_yes_no("Include digits (0-9)?"),
            "symbols": ask_yes_no("Include symbols (!@#$...)?"),
        }
        if any(options.values()):
            break
        print("  You need at least one character type. Let's try again.\n")
    options["exclude_ambiguous"] = ask_yes_no(
        "Leave out look-alike characters (I l 1 | O 0 o)?", default=False)
    count = ask_number("How many passwords", 1, 1, MAX_COUNT)

    print("\nYour password" + ("s:" if count > 1 else ":"))
    for number in range(1, count + 1):
        print(f"  {number}. {generate_password(length, **options)}")
    print(describe_strength(length, **options))


# ---------------------------------------------------------------------------
# Command-line mode
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="password_gen.py",
        description="Generate strong random passwords. "
                    "Run it without any options for interactive mode.",
    )
    parser.add_argument("-l", "--length", type=int, default=DEFAULT_LENGTH,
                        help=f"password length, {MIN_LENGTH}-{MAX_LENGTH} "
                             f"(default: {DEFAULT_LENGTH})")
    parser.add_argument("-n", "--count", type=int, default=1,
                        help=f"how many passwords to make, 1-{MAX_COUNT} (default: 1)")
    parser.add_argument("--no-upper", action="store_true", help="leave out uppercase letters")
    parser.add_argument("--no-lower", action="store_true", help="leave out lowercase letters")
    parser.add_argument("--no-digits", action="store_true", help="leave out digits")
    parser.add_argument("--no-symbols", action="store_true", help="leave out symbols")
    parser.add_argument("--exclude-ambiguous", action="store_true",
                        help=f"leave out look-alike characters ({AMBIGUOUS})")
    return parser


def main(argv=None):
    """Program entry point. Returns the exit code (0 means success)."""
    if argv is None:
        argv = sys.argv[1:]

    if not argv:  # no options given, so ask questions instead
        try:
            interactive()
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
            return 1
        return 0

    parser = build_parser()
    args = parser.parse_args(argv)
    if not MIN_LENGTH <= args.length <= MAX_LENGTH:
        parser.error(f"--length must be between {MIN_LENGTH} and {MAX_LENGTH}")
    if not 1 <= args.count <= MAX_COUNT:
        parser.error(f"--count must be between 1 and {MAX_COUNT}")

    options = {
        "upper": not args.no_upper,
        "lower": not args.no_lower,
        "digits": not args.no_digits,
        "symbols": not args.no_symbols,
        "exclude_ambiguous": args.exclude_ambiguous,
    }
    if not any((options["upper"], options["lower"], options["digits"], options["symbols"])):
        parser.error("you switched off every character type; keep at least one")

    for _ in range(args.count):
        print(generate_password(args.length, **options))
    # The strength line goes to stderr, so stdout holds only passwords
    # (handy for piping, e.g.  python password_gen.py | clip  on Windows).
    print(describe_strength(args.length, **options), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
