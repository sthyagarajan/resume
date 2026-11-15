#!/usr/bin/env python3
"""Extract text from the submitted resume PDF.

Chrome's headless print embeds subset CID fonts. pdftotext is not installed
here, so this reads Flate streams and each font's ToUnicode map.
"""

import re
import sys
import zlib
from pathlib import Path


def find_objects(data: bytes) -> dict[int, bytes]:
    objects = {}
    for match in re.finditer(rb"(?m)^(\d+) 0 obj\b", data):
        number = int(match.group(1))
        start = match.end()
        end = data.find(b"\nendobj", start)
        if end == -1:
            continue
        objects[number] = data[start:end]
    return objects


def stream_bytes(obj: bytes) -> bytes | None:
    match = re.search(rb"/Length\s+(\d+)\s*>>\s*stream\r?\n", obj)
    if not match:
        return None
    length = int(match.group(1))
    raw = obj[match.end() : match.end() + length]
    if b"/FlateDecode" in obj[: match.start() + 80] or b"/FlateDecode" in obj:
        return zlib.decompress(raw)
    return raw


def parse_cmap(cmap: str) -> dict[int, str]:
    mapping: dict[int, str] = {}

    def dest_text(token: str) -> str:
        hex_bytes = bytes.fromhex(token)
        return hex_bytes.decode("utf-16-be")

    for block in re.finditer(
        r"(\d+)\s+beginbfchar\s*(.*?)\s*endbfchar", cmap, re.S
    ):
        for src, dst in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", block.group(2)):
            mapping[int(src, 16)] = dest_text(dst)

    for block in re.finditer(
        r"(\d+)\s+beginbfrange\s*(.*?)\s*endbfrange", cmap, re.S
    ):
        for line in block.group(2).splitlines():
            line = line.strip()
            if not line:
                continue
            parts = re.findall(r"<([0-9A-Fa-f]+)>|\[(.*?)\]", line)
            if len(parts) >= 3 and parts[2][0]:
                start, end = int(parts[0][0], 16), int(parts[1][0], 16)
                first = dest_text(parts[2][0])
                for offset, code in enumerate(range(start, end + 1)):
                    if not first:
                        continue
                    last = first[-1]
                    mapping[code] = first[:-1] + chr(ord(last) + offset)
            elif len(parts) >= 3 and parts[2][1]:
                start = int(parts[0][0], 16)
                dests = re.findall(r"<([0-9A-Fa-f]+)>", parts[2][1])
                for offset, dest in enumerate(dests):
                    mapping[start + offset] = dest_text(dest)
    return mapping


def decode_glyph(font_map: dict[int, str], hex_text: str) -> str:
    raw = bytes.fromhex(hex_text)
    if len(raw) % 2:
        raw = raw[1:]
    chars = []
    for index in range(0, len(raw), 2):
        code = int.from_bytes(raw[index : index + 2], "big")
        chars.append(font_map.get(code, ""))
    return "".join(chars)


def decode_literal(token: str) -> str:
    out = []
    index = 0
    while index < len(token):
        char = token[index]
        if char != "\\":
            out.append(char)
            index += 1
            continue
        index += 1
        if index >= len(token):
            break
        escaped = token[index]
        out.append({"n": "\n", "r": "\r", "t": "\t", "b": "\b", "f": "\f"}.get(escaped, escaped))
        index += 1
    return "".join(out)


def font_maps(objects: dict[int, bytes]) -> dict[str, dict[int, str]]:
    maps = {}
    for number, obj in objects.items():
        if b"/Type /Font" not in obj or b"/ToUnicode" not in obj:
            continue
        name_match = re.search(rb"/BaseFont\s*/([^\s/>]+)", obj)
        unicode_match = re.search(rb"/ToUnicode\s+(\d+)\s+0 R", obj)
        if not name_match or not unicode_match:
            continue
        cmap_obj = objects.get(int(unicode_match.group(1)))
        if cmap_obj is None:
            continue
        cmap_stream = stream_bytes(cmap_obj)
        if cmap_stream is None:
            continue
        # Page resources name fonts /F4, /F5, ... which are the Type0 objects.
        maps[f"F{number}"] = parse_cmap(cmap_stream.decode("latin1"))
    return maps


LIGATURES = str.maketrans(
    {
        "\u00a0": " ",
        "\ufb00": "ff",
        "\ufb01": "fi",
        "\ufb02": "fl",
        "\ufb03": "ffi",
        "\ufb04": "ffl",
    }
)


def normalize(text: str) -> str:
    return " ".join(text.translate(LIGATURES).split())


def extract_page(content: str, fonts: dict[str, dict[int, str]]) -> list[str]:
    lines: list[str] = []
    current_font = ""
    buffer = ""
    last_y = None
    pending_gap = False

    def flush() -> None:
        nonlocal buffer, pending_gap
        text = normalize(buffer)
        if text:
            lines.append(text)
        buffer = ""
        pending_gap = False

    def append(piece: str) -> None:
        nonlocal buffer, pending_gap
        if pending_gap and buffer and piece:
            if not buffer[-1].isspace() and piece[0] not in " ,.;:)]>—–-":
                buffer += " "
        pending_gap = False
        buffer += piece

    tokens = re.finditer(
        r"/(F\d+)\s+[0-9.]+\s+Tf"
        r"|1 0 0 -1\s+([0-9.]+)\s+([0-9.]+)\s+Tm"
        r"|<([0-9A-Fa-f]+)>\s*Tj"
        r"|\((?:\\.|[^\\)])*\)\s*Tj",
        content,
    )
    for token in tokens:
        if token.group(1):
            current_font = token.group(1)
            continue
        if token.group(2):
            y = float(token.group(3))
            if last_y is not None and abs(y - last_y) > 1.5:
                flush()
            elif buffer:
                pending_gap = True
            last_y = y
            continue
        if token.group(4) is not None:
            append(decode_glyph(fonts.get(current_font, {}), token.group(4)))
            continue
        literal = token.group(0)[1 : token.group(0).rfind(")")]
        append(decode_literal(literal))
    flush()
    return lines


def page_count(objects: dict[int, bytes]) -> int:
    for obj in objects.values():
        match = re.search(rb"/Type\s*/Pages\b.*?/Count\s+(\d+)", obj, re.S)
        if match:
            return int(match.group(1))
    return 1


def extract(path: Path) -> str:
    data = path.read_bytes()
    objects = find_objects(data)
    fonts = font_maps(objects)
    pages = []
    for obj in objects.values():
        if b"/Type /Page" not in obj or b"/Contents" not in obj:
            continue
        content_match = re.search(rb"/Contents\s+(\d+)\s+0 R", obj)
        if not content_match:
            continue
        content_obj = objects.get(int(content_match.group(1)))
        if content_obj is None:
            continue
        content = stream_bytes(content_obj)
        if content is None:
            continue
        pages.append("\n".join(extract_page(content.decode("latin1"), fonts)))
    if not pages or not any(page.strip() for page in pages):
        raise SystemExit(f"no text extracted from {path}")
    header = f"pages: {page_count(objects)}"
    return header + "\n\n" + "\n\n".join(pages)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} FILE.pdf")
    print(extract(Path(sys.argv[1])))


if __name__ == "__main__":
    main()
