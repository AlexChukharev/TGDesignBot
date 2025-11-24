import json
from pathlib import Path

LANG_FILE = Path("Data/user_lang.json")
DEFAULT_LANG = "ru"

user_lang: dict[str, str] = {}


def load_user_langs() -> None:
    global user_lang
    if LANG_FILE.exists():
        with LANG_FILE.open("r", encoding="utf-8") as f:
            user_lang = json.load(f)
    else:
        user_lang = {}


def save_user_langs() -> None:
    LANG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LANG_FILE.open("w", encoding="utf-8") as f:
        json.dump(user_lang, f, ensure_ascii=False, indent=2)


def get_user_lang(user_id: int) -> str | None:
    """
    Возвращает 'ru', 'en' или None,
    если пользователь ещё не выбрал язык
    """
    return user_lang.get(str(user_id))


def set_user_lang(user_id: int, lang: str) -> None:
    user_lang[str(user_id)] = lang
    save_user_langs()
