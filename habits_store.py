import json
from pathlib import Path
import tempfile
import os

class HabitStore:
    VERSION = 1
    def __init__(self, path):
        self.path = Path(path)
        self.data = {}
        if self.path.exists():
            raw = json.loads(self.path.read_text(encoding='utf-8'))
            if not isinstance(raw, dict):
                raise ValueError('Habit file must contain an object')
            if 'version' in raw:
                if raw['version'] != self.VERSION or not isinstance(raw.get('habits'), dict):
                    raise ValueError('Unsupported or invalid habit schema')
                self.data = raw['habits']
            else:
                # Legacy values remain selectors; migrate only on a successful save.
                self.data = {domain: {intent: {'selector': value} if isinstance(value, str) else value
                              for intent, value in intents.items()} for domain, intents in raw.items()
                             if isinstance(intents, dict)}
    def get(self, domain, intent):
        entry = self.data.get(domain, {}).get(intent)
        return entry.get('selector') if isinstance(entry, dict) else None
    def save(self, domain, intent, selector):
        updated = {**self.data, domain: {**self.data.get(domain, {}), intent: {'selector': selector}}}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp = tempfile.mkstemp(dir=self.path.parent, prefix='.habits-', suffix='.tmp')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump({'version': self.VERSION, 'habits': updated}, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp, self.path)
            self.data = updated
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
