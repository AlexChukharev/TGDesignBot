from __future__ import annotations
import glob, os, time, threading
from typing import Dict, Optional

import yaml


class _SafeDict(dict):
    def __missing__(self, k):  # оставит {placeholder}, если не передан
        return "{" + k + "}"


class TextStore:
    """
    Простой in-memory стор текстов из YAML.
    Формат файла:
    ---
    prefix: no_access
    messages:
      no_access:
        ru: |
          Привет!
          ...
        en: |
          Hi!
          ...
    """
    def __init__(self, directory: str, default_lang: str = "ru", check_every: float = 0.0):
        self.directory = directory
        self.default_lang = default_lang
        self._messages: Dict[str, Dict[str, str]] = {}  # key -> {lang: text}
        self._mtimes: Dict[str, float] = {}
        self._lock = threading.RLock()
        self._load_all()

        if check_every and check_every > 0:
            t = threading.Thread(target=self._watch, args=(check_every,), daemon=True)
            t.start()

    def get(self, key: str, lang: str, **params) -> str:
        """Вернёт текст по ключу/языку с фоллбэком и подстановкой параметров."""
        with self._lock:
            lang_map = self._messages.get(key)
            if not lang_map:
                return f"[{key}]"
            txt = lang_map.get(lang) or lang_map.get(self.default_lang)
            if txt is None:
                return f"[{key}]"
        return txt.format_map(_SafeDict(params))

    def has(self, key: str) -> bool:
        with self._lock:
            return key in self._messages

    def keys(self):
        with self._lock:
            return list(self._messages.keys())

    # ---- загрузка и хот-релоад ----
    def _watch(self, period: float):
        while True:
            try:
                if self._changed():
                    self._load_all()
            except Exception:
                pass
            time.sleep(period)

    def _files(self):
        files = []
        for ext in ("*.yaml", "*.yml"):
            files.extend(glob.glob(os.path.join(self.directory, ext)))
        files.sort()
        return files

    def _changed(self) -> bool:
        files = self._files()
        if set(files) != set(self._mtimes.keys()):
            return True
        for p in files:
            try:
                m = os.path.getmtime(p)
            except FileNotFoundError:
                return True
            if self._mtimes.get(p) != m:
                return True
        return False

    def _load_all(self):
        new_messages: Dict[str, Dict[str, str]] = {}
        new_mtimes: Dict[str, float] = {}

        for path in self._files():
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            prefix = (data.get("prefix") or "").strip()
            msgs = data.get("messages") or {}
            if not isinstance(msgs, dict):
                continue

            for short_key, lang_map in msgs.items():
                if not isinstance(lang_map, dict):
                    continue
                full_key = f"{prefix}.{short_key}" if prefix else str(short_key)
                bucket = new_messages.setdefault(full_key, {})
                for lang, text in lang_map.items():
                    if isinstance(text, str):
                        bucket[lang] = text

            try:
                new_mtimes[path] = os.path.getmtime(path)
            except FileNotFoundError:
                continue

        with self._lock:
            self._messages = new_messages
            self._mtimes = new_mtimes


# наше глобальное хранилище текстов, файлы пересчитываются раз в полчаса
store = TextStore(directory="CONFIG/texts", default_lang="ru", check_every=1800.0)