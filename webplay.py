#!/usr/bin/env python3

"""This program generates a webpage for a play written in a text file."""

import re
import sys


LANG = None
TITLE = "Play"
CSS_HREF: list[str] = []
JS_SRC: list[str] = []
HEADER_COMPLETE = False
CHARACTERS: dict[str, str] = {}

RE_H2 = re.compile(r"^@!!(.+)$")
RE_H1 = re.compile(r"^@!(.+)$")
RE_RAW = re.compile(r"^@~(.+)$")
RE_CHARACTER = re.compile(r"^@([^:]+):\s*(.+)$")
RE_DIALOGUE = re.compile(r"^([^:]+):\s*(.+)$")

RE_IMG = re.compile(r"\[img!(\S+) (.+?)\]")
RE_IMG_SUB = r'<img src="\1" alt="\2">'

RE_NON_CLASS_IDENTIFIER = re.compile(r"[^a-z0-9_-]", flags=re.IGNORECASE)


def print_header() -> None:
    """Print the beginning of the HTML document."""
    lang = f' lang="{LANG}"' if LANG else ""

    print(
        f"""<!DOCTYPE html>
<html{lang}>
<head>
<title>{TITLE}</title>"""
    )

    for css_href in CSS_HREF:
        print(f"""<link rel="stylesheet" href="{css_href}">""")

    for js_src in JS_SRC:
        print(f"""<script type="text/javascript" src="{js_src}"></script>""")

    print("""<body>""")


def print_footer() -> None:
    """Print the end of the HTML document."""
    print(
        """</body>
</html>"""
    )


def make_replacements(text: str) -> str:
    """Add HTML classes and descriptions to character names."""
    if len(CHARACTERS) > 0:
        pattern = "|".join(map(lambda name: rf"\b{name}\b", CHARACTERS.keys()))
        text = re.sub(pattern, lambda match: CHARACTERS[match.group()], text)
    text = RE_IMG.sub(RE_IMG_SUB, text)
    return text


def make_class_name(name: str) -> str:
    """Transform a character name into a CSS class name-friendly format."""
    return RE_NON_CLASS_IDENTIFIER.sub("-", name)


# pylint: disable=global-statement
def process_line(line: str) -> None:
    """Process a character description or line of content."""

    global HEADER_COMPLETE, TITLE

    # Pattern-match the line
    #   @!TEXT
    #       Output: <h1>TEXT</h1>
    #   @!!TEXT
    #       Output: <h2>TEXT</h2>
    #   @~TEXT
    #       Output: TEXT (no automatic <p>)
    #   @NAME: TEXT
    #       Description of a character
    #       If a character by this name already exists, throw an error
    #       No output
    #       Replace all occurrences of the character's name (case-sensitive) with
    #           <span class="character NAME">NAME<span class="description">TEXT</span></span>
    #       Make all occurrences of the character's name show TEXT on hover
    #   NAME: TEXT
    #       Output: <p><span class="speaker">NAME:</span><span class="dialogue">TEXT</span></p>
    #   DEFAULT
    #       Output: <p class="notes">TEXT</p>

    match_found = False
    output = None

    match = RE_H2.search(line)
    if match:
        match_found = True
        text = match.group(1)
        output = f"<h2>{text}</h2>"

    match = RE_H1.search(line)
    if (not match_found) and match:
        match_found = True
        text = match.group(1)
        output = f"<h1>{text}</h1>"

        if TITLE == "Play":
            TITLE = text

    match = RE_RAW.search(line)
    if (not match_found) and match:
        match_found = True
        output = match.group(1)
        output = make_replacements(output)

    match = RE_CHARACTER.search(line)
    if (not match_found) and match:
        match_found = True
        name = match.group(1)
        description = match.group(2)
        description = (
            f'<span class="character {make_class_name(name)}">'
            f"{name}"
            f'<span class="description">{description}</span>'
            "</span>"
        )

        description = RE_IMG.sub(RE_IMG_SUB, description)
        CHARACTERS[name] = description

    match = RE_DIALOGUE.search(line)
    if (not match_found) and match:
        match_found = True
        name = match.group(1)
        dialogue = match.group(2)

        name_part = name
        name_part = make_replacements(name_part)
        name_part = f'<span class="speaker">{name_part}:</span>'

        dialogue_part = f'<span class="dialogue">{dialogue}</span>'
        dialogue_part = make_replacements(dialogue_part)
        dialogue_part = RE_IMG.sub(RE_IMG_SUB, dialogue_part)

        output = f"<p>{name_part}{dialogue_part}</p>"

    # Default = notes
    if not match_found:
        match_found = True
        output = f'<p class="notes">{line}</p>'
        output = make_replacements(output)

    if output:
        # Before echoing anything:
        if not HEADER_COMPLETE:
            print_header()
            HEADER_COMPLETE = True

        print(output)


def print_help() -> None:
    """Displays basic information about running the program."""
    print(f"""Usage: {sys.argv[0]} [-c CSS_HREF...] [-s JS_SRC...] [-l HTML_LANG]""")


# pylint: disable=global-statement, too-many-branches
def main() -> None:
    """Main function for the program."""

    global LANG

    line = ""

    if len(sys.argv) > 1:
        getting_css_paths = False
        getting_js_paths = False
        getting_lang = False

        for arg in sys.argv[1:]:
            if arg in ["-h", "--help"]:
                print_help()
                sys.exit(0)
            elif arg == "-c":
                getting_css_paths = True
                getting_js_paths = False
                getting_lang = False
                continue
            elif arg == "-s":
                getting_css_paths = False
                getting_js_paths = True
                getting_lang = False
                continue
            elif arg == "-l":
                getting_css_paths = False
                getting_js_paths = False
                getting_lang = True
                continue

            if getting_css_paths:
                CSS_HREF.append(arg)
            elif getting_js_paths:
                JS_SRC.append(arg)
            elif getting_lang:
                LANG = arg
                getting_lang = False
            else:
                print(f"Unknown argument {arg}", file=sys.stderr)
                sys.exit(1)

    for next_line in sys.stdin:
        next_line = next_line.strip()
        if next_line != "":
            # Ignore comments
            if next_line[0] == "#":
                continue

            # If adding to the previous line, add a space in between
            if line != "":
                line += " "

            line += next_line
        else:
            if line != "":
                process_line(line)
            line = ""

    # Handle the case where no newline is at the end of the file
    if line != "":
        process_line(line)

    if HEADER_COMPLETE:
        print_footer()


if __name__ == "__main__":
    main()
