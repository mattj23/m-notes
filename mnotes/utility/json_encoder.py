"""
    A custom JSON encoder to handle the fact that python's json module doesn't encode datetimes by default
"""

import json
from datetime import datetime as DateTime
from mnotes.notes.markdown_notes import MetaData


class MNotesEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, DateTime):
            return o.isoformat()
        elif isinstance(o, MetaData):
            return f"MetaData.{o.name}"

        return json.JSONEncoder.default(self, o)


class MNotesDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.try_decode_others, *args, **kwargs)

    @staticmethod
    def try_decode_others(d):
        decoded = {}
        for k, v in d.items():
            if isinstance(v, str) and v.startswith("MetaData."):
                try:
                    decoded[k] = MetaData[v.replace("MetaData.", "")]
                except KeyError:
                    decoded[k] = v
            else:
                try:
                    decoded[k] = DateTime.fromisoformat(v)
                except (ValueError, TypeError):
                    decoded[k] = v

        return decoded
