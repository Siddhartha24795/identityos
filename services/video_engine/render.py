"""v4.2 — renders a video statement SCRIPT (services/video_engine/generate.py)
into a narrated DRAFT: generic text slides (Playwright, already a project
dependency) plus synthesized narration (SVOX Pico TTS) assembled into an
.mp4 (ffmpeg). This is a timing/content draft, not a submission-ready
video — see the module docstring in generate.py for the full scope
boundary. Every rendered slide carries a burned-in disclosure banner so
the warning travels with the file even if it's shared outside this repo.

Optional system dependencies, NOT required by `make setup` / `make test`:
  - `pico2wave` (Debian/Ubuntu: `apt-get install libttspico-utils`)
  - `ffmpeg`
Both are checked explicitly; missing either raises a clear, actionable
RuntimeError rather than failing deep inside a subprocess call.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from packages.schemas.document import GeneratedDocument

DISCLOSURE_BANNER = "AI-DRAFTED SCRIPT — READ FOR TIMING ONLY — RECORD YOURSELF FOR SUBMISSION"


def _clean_for_narration(text: str) -> str:
    """Strips citation brackets (a spoken script shouldn't read
    "[resume:014]" aloud -- the written script in documents/*.md remains
    the source of truth) and replaces "--"/em-dash/en-dash punctuation
    with a comma. pico2wave reads a literal "--" as "hyphen hyphen" --
    found by ear in an early render of this project's own solution video,
    which used " -- " as an em-dash substitute in its narration script."""
    cleaned = re.sub(r"\[[^\]]+\]\s*", "", text).strip()
    cleaned = re.sub(r"\s*(--|—|–)\s*", ", ", cleaned)
    return cleaned

_SLIDE_HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
  body {{ margin:0; width:1280px; height:720px; background:#0b1120; color:#eef2f7;
         font-family:-apple-system,'Segoe UI',sans-serif; }}
  .frame {{ padding:64px 76px; height:100%; box-sizing:border-box; display:flex;
            flex-direction:column; justify-content:center; }}
  .kicker {{ color:#5eead4; font-size:18px; font-weight:700; letter-spacing:3px;
             text-transform:uppercase; margin-bottom:18px; }}
  .text {{ font-size:30px; line-height:1.5; max-width:1100px; }}
  .banner {{ position:absolute; left:0; right:0; bottom:0; background:#3a1420;
             color:#fb7185; font-size:16px; font-weight:700; text-align:center;
             padding:14px; letter-spacing:1px; }}
</style></head>
<body>
<div class="frame">
  <div class="kicker">{section_name}</div>
  <div class="text">{text}</div>
</div>
<div class="banner">{banner}</div>
</body></html>"""


def _require_tool(name: str, install_hint: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(
            f"render_narrated_draft() needs '{name}' on PATH, which is not installed. "
            f"Install it with: {install_hint}. This is an optional capability, not "
            f"required for any other IdentityOS command."
        )


def render_narrated_draft(document: GeneratedDocument, out_dir: Path, tag: str) -> dict:
    """Renders one narrated draft .mp4 per document, from its sections.
    Returns a dict summary (path, per-section durations, total duration).
    Raises RuntimeError with an actionable message if pico2wave or ffmpeg
    is missing -- never silently degrades or fabricates a placeholder video.
    """
    _require_tool("pico2wave", "apt-get install libttspico-utils (Debian/Ubuntu)")
    _require_tool("ffmpeg", "apt-get install ffmpeg (Debian/Ubuntu) or brew install ffmpeg (macOS)")

    from playwright.sync_api import sync_playwright  # local import: optional dependency path

    out_dir = Path(out_dir)
    work_dir = out_dir / f"_render_{document.system_name}"
    work_dir.mkdir(parents=True, exist_ok=True)

    segment_paths = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        for i, section in enumerate(document.sections):
            slide_path = work_dir / f"{i:02d}_{section.section_name}.png"
            wav_path = work_dir / f"{i:02d}_{section.section_name}.wav"
            seg_path = work_dir / f"{i:02d}_{section.section_name}.mp4"

            speakable = _clean_for_narration(section.text)

            page.set_content(_SLIDE_HTML.format(
                section_name=section.section_name.replace("_", " ").upper(),
                text=speakable[:600],
                banner=DISCLOSURE_BANNER,
            ))
            page.screenshot(path=str(slide_path))

            subprocess.run(
                ["pico2wave", "-l", "en-US", "-w", str(wav_path), speakable or "No content generated for this section."],
                check=True, capture_output=True,
            )
            subprocess.run(
                ["ffmpeg", "-y", "-loop", "1", "-i", str(slide_path), "-i", str(wav_path),
                 "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
                 "-vf", "fps=25,scale=1280:720", "-c:a", "aac", "-b:a", "160k",
                 "-shortest", str(seg_path)],
                check=True, capture_output=True,
            )
            segment_paths.append(seg_path)
        browser.close()

    concat_list = work_dir / "concat.txt"
    # ffmpeg's concat demuxer resolves relative paths against the list
    # file's own directory, not the caller's cwd -- must be absolute.
    concat_list.write_text(
        "".join(f"file '{p.resolve()}'\n" for p in segment_paths), encoding="utf-8"
    )
    final_path = out_dir / f"{tag}__{document.system_name}_video_statement_draft.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
         "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
         str(final_path)],
        check=True, capture_output=True,
    )
    duration = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(final_path)]
    ).strip())

    return {
        "output_path": str(final_path),
        "n_sections": len(document.sections),
        "duration_seconds": round(duration, 2),
        "disclosure": DISCLOSURE_BANNER,
    }
