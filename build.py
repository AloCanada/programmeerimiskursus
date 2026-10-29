from __future__ import annotations

import argparse
import html
import re
import shutil
import urllib.request
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).parent
SOURCE_DIR = ROOT / "Materjalid"
OUTPUT_DIR = ROOT / "site"
IMAGE_DIR = OUTPUT_DIR / "assets" / "images"
BRANDING_DIR = ROOT / "assets" / "branding"
IMAGE_PATTERN = re.compile(r'(?P<prefix>\bsrc\s*=\s*["\'])(?P<url>https?://[^"\']+)(?P<suffix>["\'])', re.I)
LOCAL_IMAGES = {
    "https://i0.wp.com/randomnerdtutorials.com/wp-content/uploads/2022/04/ESP32-URL-Arduino-IDE.png?w=828&quality=100&strip=all&ssl=1": "arduino-ide-esp32-url.png",
    "https://moodle.taltech.ee/draftfile.php/685804/user/draft/228243530/Screenshot%202025-10-13%20at%2018.52.52%20%281%29.png": "arduino-ide-screenshot-1.png",
    "https://moodle.taltech.ee/draftfile.php/685804/user/draft/228243530/Screenshot%202025-10-13%20at%2018.54.22.png": "arduino-ide-screenshot-2.png",
    "https://moodle.taltech.ee/draftfile.php/685804/user/draft/928663207/blokkdiagramm%201.2.drawio.png": "n-idiskood-blokkdiagramm.png",
    "https://upload.wikimedia.org/wikipedia/commons/0/02/PWM_duty_cycle_with_label.gif?utm_source=et.wikipedia.org&utm_campaign=index&utm_content=original": "pwm-duty-cycle.gif",
}
CODE_PATTERN = re.compile(r"(?P<comment>//[^\n]*|/\*[\s\S]*?\*/)|(?P<string>\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')|(?P<preprocessor>^[ \t]*#[^\n]*)|(?P<number>\b\d+(?:\.\d+)?\b)|(?P<keyword>\b(?:auto|bool|break|case|const|continue|default|do|else|for|if|int|long|return|short|static|struct|switch|unsigned|void|while)\b)|(?P<type>\b(?:HIGH|LOW|INPUT|OUTPUT|INPUT_PULLUP|String|uint8_t|true|false)\b)|(?P<function>\b[a-zA-Z_]\w*(?=\s*\())", re.M)


@dataclass(frozen=True)
class Lesson:
    source: Path
    slug: str
    title: str


def title_from_filename(path: Path) -> str:
    return re.sub(r"^\d+[.)]?\s*", "", path.stem).strip()


def slug_from_title(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower(), flags=re.ASCII).strip("-")
    return slug or "materjal"


def lessons() -> list[Lesson]:
    files = sorted(SOURCE_DIR.glob("*.txt"), key=lambda path: (int(re.match(r"\d+", path.stem).group()) if re.match(r"\d+", path.stem) else 999, path.name))
    return [Lesson(path, slug_from_title(title_from_filename(path)), title_from_filename(path)) for path in files]


def localize_images(fragment: str, lesson: Lesson, warnings: list[str]) -> str:
    def replace(match: re.Match[str]) -> str:
        url = html.unescape(match.group("url"))
        local_name = LOCAL_IMAGES.get(url)
        if local_name and (ROOT / "assets" / "images" / local_name).exists():
            shutil.copyfile(ROOT / "assets" / "images" / local_name, IMAGE_DIR / local_name)
            return f'{match.group("prefix")}assets/images/{local_name}{match.group("suffix")}'
        suffix = Path(url.split("?", 1)[0]).suffix.lower() or ".img"
        image_name = f"{lesson.slug}-{len(list(IMAGE_DIR.glob(f'{lesson.slug}-*'))) + 1}{suffix}"
        destination = IMAGE_DIR / image_name
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "programmeerimiskursus-site-builder/1.0"})
            with urllib.request.urlopen(request, timeout=15) as response:
                destination.write_bytes(response.read())
        except Exception as error:
            warnings.append(f"{lesson.source.name}: pilti ei saanud alla laadida ({url}): {error}")
            return match.group(0)
        return f'{match.group("prefix")}assets/images/{image_name}{match.group("suffix")}'

    return IMAGE_PATTERN.sub(replace, fragment)


def highlight_code(match: re.Match[str]) -> str:
    source = re.sub(r"</?[a-zA-Z][^>]*>", "", html.unescape(match.group(1)))
    highlighted: list[str] = []
    position = 0
    for token in CODE_PATTERN.finditer(source):
        highlighted.append(html.escape(source[position:token.start()]))
        token_type = next(name for name, value in token.groupdict().items() if value is not None)
        highlighted.append(f'<span class="code-{token_type}">{html.escape(token.group())}</span>')
        position = token.end()
    highlighted.append(html.escape(source[position:]))
    return f'<pre><code class="language-cpp">{"".join(highlighted)}</code></pre>'


def highlight_code_blocks(fragment: str) -> str:
    return re.sub(r"<pre>\s*<code(?:\s+class=\"[^\"]*\")?>([\s\S]*?)</code>\s*</pre>", highlight_code, fragment, flags=re.I)


def navigation(items: list[Lesson], current: Lesson | None = None) -> str:
    links = "\n".join(
        f'<a class="lesson-link{" is-active" if current and item.slug == current.slug else ""}" href="{item.slug}.html">{html.escape(item.title)}</a>'
        for item in items
    )
    return f'<nav class="lesson-nav" aria-label="Õppematerjalid"><a class="lesson-link{" is-active" if current is None else ""}" href="index.html">Ülevaade</a>{links}</nav>'


def copy_logo() -> str:
    for extension in (".png", ".jpg", ".jpeg", ".svg", ".webp"):
        source = BRANDING_DIR / f"robotiklubi-logo{extension}"
        if source.exists():
            destination = OUTPUT_DIR / "assets" / "branding" / source.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            return f'<img class="brand-logo" src="assets/branding/{source.name}" alt="Robotiklubi logo">'
    return '<span class="brand-mark" aria-hidden="true">RK</span>'


def document(title: str, body: str, nav: str, show_nav: bool = True) -> str:
    layout_class = "layout" if show_nav else "layout layout--overview"
    sidebar = f'<aside id="site-nav" class="sidebar">{nav}</aside>' if show_nav else ""
    menu_button = '<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menüü</button>' if show_nav else ""
    logo = copy_logo()
    return f"""<!doctype html>
<html lang="et">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} | Robotiklubi programmeerimiskursus</title>
  <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
  <header class="site-header">
    <a class="brand" href="index.html">{logo}<span>Robotiklubi<br><strong>programmeerimiskursus</strong></span></a>
    {menu_button}
  </header>
  <div class="{layout_class}">
    {sidebar}
    <main class="content">{body}</main>
  </div>
  <script src="assets/app.js" defer></script>
</body>
</html>
"""


def build() -> int:
    parser = argparse.ArgumentParser(description="Genereeri programmeerimiskursuse staatiline veeb.")
    parser.add_argument("--no-download", action="store_true", help="Ära laadi väliseid pilte alla.")
    args = parser.parse_args()
    items = lessons()
    if not items:
        raise SystemExit("Materjalid-kaustas ei ole .txt materjale.")
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    IMAGE_DIR.mkdir(parents=True)
    (OUTPUT_DIR / "assets" / "styles.css").write_text((ROOT / "assets" / "styles.css").read_text(encoding="utf-8"), encoding="utf-8")
    (OUTPUT_DIR / "assets" / "app.js").write_text((ROOT / "assets" / "app.js").read_text(encoding="utf-8"), encoding="utf-8")
    warnings: list[str] = []
    cards = "\n".join(f'<a class="lesson-row" href="{item.slug}.html"><span>{index:02d}</span><h2>{html.escape(item.title)}</h2><span class="lesson-arrow" aria-hidden="true">→</span></a>' for index, item in enumerate(items, 1))
    intro = '<section class="hero"><p class="eyebrow">TalTechi fondi vaimus · Robotiklubi</p><h1>Programmeerimine, mis liigub päriselus.</h1><p>Praktiline sissejuhatus Arduino ja ESP32 programmeerimisse. Alusta algusest või vali endale sobiv teema.</p></section><section class="lesson-list" aria-label="Kursuse materjalid">' + cards + "</section>"
    (OUTPUT_DIR / "index.html").write_text(document("Ülevaade", intro, navigation(items), show_nav=False), encoding="utf-8")
    for item in items:
        fragment = item.source.read_text(encoding="utf-8")
        if not args.no_download:
            fragment = localize_images(fragment, item, warnings)
        fragment = re.sub(r"<pre>\s*(<img\b[\s\S]*?)</pre>", r'<div class="image-frame">\1</div>', fragment, flags=re.I)
        fragment = highlight_code_blocks(fragment)
        body = f'<p class="eyebrow">Õppematerjal {items.index(item) + 1:02d}</p><h1>{html.escape(item.title)}</h1><article class="lesson-content">{fragment}</article>'
        position = items.index(item)
        previous = f'<a href="{items[position - 1].slug}.html">← Eelmine</a>' if position else "<span></span>"
        following = f'<a href="{items[position + 1].slug}.html">Järgmine →</a>' if position + 1 < len(items) else "<span></span>"
        body += f'<nav class="pager" aria-label="Materjali navigeerimine">{previous}{following}</nav>'
        (OUTPUT_DIR / f"{item.slug}.html").write_text(document(item.title, body, navigation(items, item)), encoding="utf-8")
    print(f"Genereeritud {len(items)} materjali: {OUTPUT_DIR}")
    for warning in warnings:
        print(f"HOIATUS: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
