#!/usr/bin/env python3
import sys


TITLE = "Play"
CSS_HREF: list[str] = []
JS_SRC: list[str] = []
HEADER_COMPLETE = False
CHARACTERS: dict[str, str] = {}


def print_header() -> None:
    print(
        f"""<!DOCTYPE html>
<html>
<head>
<title>{TITLE}</title>"""
    )

    for css_href in CSS_HREF:
        print(f"""<link rel="stylesheet" href="{css_href}">""")

    for js_src in JS_SRC:
        print(f"""<script type="text/javascript" src="{js_src}"></script>""")

    print("""<body>""")


def print_footer() -> None:
    print(
        """</body>
</html>"""
    )


def process_line(line: str) -> None:
    global HEADER_COMPLETE

    # Before echoing anything:
    if not HEADER_COMPLETE:
        print_header()
        HEADER_COMPLETE = True

    print(line)


def print_help() -> None:
    print(f"""Usage: {sys.argv[0]} [-c CSS_HREF...] [-s JS_SRC...]""")


def main() -> None:
    line = ""

    if len(sys.argv) > 1:
        getting_css_paths = False
        getting_js_paths = False

        for arg in sys.argv[1:]:
            if arg in ["-h", "--help"]:
                print_help()
                sys.exit(0)
            elif arg == "-c":
                getting_css_paths = True
                getting_js_paths = False
                continue
            elif arg == "-s":
                getting_css_paths = False
                getting_js_paths = True
                continue

            if getting_css_paths:
                CSS_HREF.append(arg)
            elif getting_js_paths:
                JS_SRC.append(arg)
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
