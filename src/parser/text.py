from collections import defaultdict


class TextParser:
    def __init__(self, path: str):
        self.path = path

    def get_dict(self):
        d: dict[str, list[tuple[str, str, str]]] = {}
        current_key = ""
        with open(self.path, "r", encoding="utf-8") as f:
            while line := f.readline():
                text = line.strip()
                if text != "":
                    if text.startswith("//"):
                        if text not in d:
                            d[text[2:]] = []
                            current_key = text[2:]
                    else:
                        if '@' in text and len(text.split('@')) == 3:
                            title, url, time = text.split('@')
                            d[current_key].append((title, url, time.replace('/', '-').replace('_', '-')))

        return d
