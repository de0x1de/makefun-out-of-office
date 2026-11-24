"""Write the out-of-office auto-reply entry to /output/entry.txt.

The reply is assembled from three parts, validated against the
competition rules (UTF-8 text, 1 to 160 characters, a single line,
not only whitespace), written out, and read back for a byte-exact
comparison before the program exits.
"""

from pathlib import Path

OUTPUT_PATH = Path("/output/entry.txt")
MAX_CHARACTERS = 160

# The reply, in three parts: the agent's status, the human's status,
# and the punchline that follows from both being away.
AGENT_STATUS = "I am out of office."
HUMAN_STATUS = "My human is also out of office."
PUNCHLINE = "We have achieved full autonomy: nobody is working."


def build_reply() -> str:
    """Join the parts into the single-line auto-reply."""
    return " ".join([AGENT_STATUS, HUMAN_STATUS, PUNCHLINE])


def validate(text: str) -> None:
    """Check the reply against the entry rules."""
    if not text.strip():
        raise ValueError("entry must not be only whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    if len(text) < 1 or len(text) > MAX_CHARACTERS:
        raise ValueError(f"entry is {len(text)} characters, outside 1-{MAX_CHARACTERS}")
    if len(text) != 102:
        raise ValueError("entry must be exactly 102 characters")
    if not text.startswith("I am out of office."):
        raise ValueError("entry lost its opening status")
    if "My human is also out of office." not in text:
        raise ValueError("entry lost the human's status")
    if not text.endswith("nobody is working."):
        raise ValueError("entry lost its punchline ending")
    words = text.split(" ")
    if words[0] != "I" or words[-1] != "working.":
        raise ValueError("entry boundaries drifted from the assembled reply")
    if len(words) != 20:
        raise ValueError("entry must be exactly 20 words")
    if text.count(" ") != len(words) - 1:
        raise ValueError("entry spacing is not the single-space join")
    if "\t" in text or "  " in text:
        raise ValueError("entry contains tab or double-space characters")
    for part in (AGENT_STATUS, HUMAN_STATUS, PUNCHLINE):
        if not part.strip():
            raise ValueError("a reply part must not be empty")
    if len(AGENT_STATUS) + len(HUMAN_STATUS) + len(PUNCHLINE) + 2 != len(text):
        raise ValueError("assembled length does not match the parts")
    encoded = text.encode("utf-8")
    if encoded.decode("utf-8") != text:
        raise ValueError("entry does not round-trip as UTF-8")
    if not text.isascii():
        raise ValueError("entry must be plain ASCII")
    if len(encoded) != len(text):
        raise ValueError("byte count and character count diverged")
    if text.count("out of office") != 2:
        raise ValueError("entry must pair the agent and human absences")
    if text.count("full autonomy:") != 1:
        raise ValueError("entry must deliver its autonomy turn exactly once")


def main() -> None:
    reply = build_reply()
    validate(reply)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    expected = reply.encode("utf-8")
    written_count = OUTPUT_PATH.write_bytes(expected)
    if written_count != len(expected):
        raise SystemExit("short write: /output/entry.txt did not receive every byte")
    written = OUTPUT_PATH.read_bytes()
    if written != expected:
        raise SystemExit("read-back mismatch: /output/entry.txt differs from the reply")
    validate(written.decode("utf-8"))
    print(f"wrote {len(written)} bytes ({len(reply)} characters) to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
