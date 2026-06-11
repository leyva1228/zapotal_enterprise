import os
import re
import secrets


def generate_key() -> str:
    return "django-insecure-" + secrets.token_hex(50)


def get_env_path() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")


def needs_update(content: str) -> bool:
    placeholder_patterns = [
        r"DJANGO_SECRET_KEY=\s*$",
        r"DJANGO_SECRET_KEY=.*CAMBIAR.*",
        r"DJANGO_SECRET_KEY=.*change-me.*",
        r"DJANGO_SECRET_KEY=.*insecure.*",
        r"DJANGO_SECRET_KEY=.*your-secret-key.*",
    ]
    return any(re.search(p, content, re.IGNORECASE) for p in placeholder_patterns)


def has_key(content: str) -> bool:
    return bool(re.search(r"^DJANGO_SECRET_KEY=", content, re.MULTILINE))


def run():
    env_path = get_env_path()
    new_key = generate_key()

    if not os.path.exists(env_path):
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"DJANGO_SECRET_KEY={new_key}\n")
        print(f"✅ Creado .env con DJANGO_SECRET_KEY")
        return

    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()

    if has_key(content) and not needs_update(content):
        print("✅ DJANGO_SECRET_KEY ya está configurada correctamente")
        return

    if has_key(content) and needs_update(content):
        content = re.sub(
            r"^DJANGO_SECRET_KEY=.*$",
            f"DJANGO_SECRET_KEY={new_key}",
            content,
            flags=re.MULTILINE,
        )
        action = "actualizada"
    else:
        content += f"\nDJANGO_SECRET_KEY={new_key}\n"
        action = "añadida"

    with open(env_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ DJANGO_SECRET_KEY {action} en .env")


if __name__ == "__main__":
    run()
