#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path


def api_json(url: str) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "OwnFonts-CI",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def download(url: str, dest: Path) -> None:
    headers = {"User-Agent": "OwnFonts-CI"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as r, dest.open("wb") as f:
        shutil.copyfileobj(r, f)


def extract(asset: Path, dest: Path) -> None:
    lower = asset.name.lower()
    if lower.endswith(".zip"):
        with zipfile.ZipFile(asset) as zf:
            zf.extractall(dest)
    elif lower.endswith(".7z"):
        subprocess.run(["7z", "x", "-y", f"-o{dest}", str(asset)], check=True)
    elif lower.endswith((".tar.gz", ".tgz", ".tar.xz", ".txz")):
        with tarfile.open(asset) as tf:
            tf.extractall(dest)
    elif lower.endswith((".ttf", ".otf")):
        shutil.copy2(asset, dest / asset.name)
    else:
        raise RuntimeError(f"Unsupported release asset: {asset.name}")


def expand_pattern(pattern: str, tag: str) -> re.Pattern[str]:
    version = tag[1:] if tag.startswith("v") else tag
    pattern = pattern.replace("{tag}", re.escape(tag))
    pattern = pattern.replace("{version}", re.escape(version))
    return re.compile(pattern)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/fonts.json")
    ap.add_argument("--family", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text())
    family = cfg[args.family]
    repo = family["repo"]
    asset_re = expand_pattern(family["asset_regex"], args.tag)
    file_re = re.compile(family["file_regex"])

    tag_q = urllib.parse.quote(args.tag, safe="")
    release = api_json(f"https://api.github.com/repos/{repo}/releases/tags/{tag_q}")
    assets = [a for a in release.get("assets", []) if asset_re.fullmatch(a["name"])]
    if not assets:
        names = ", ".join(a["name"] for a in release.get("assets", []))
        raise SystemExit(
            f"No release asset matched {asset_re.pattern!r} for {repo}@{args.tag}. "
            f"Available assets: {names}"
        )

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="ownfonts-") as td:
        td = Path(td)
        extracted = td / "extracted"
        extracted.mkdir()
        for asset in assets:
            local = td / asset["name"]
            print(f"Downloading {repo}@{args.tag}: {asset['name']}")
            download(asset["browser_download_url"], local)
            extract(local, extracted)

        selected: list[Path] = []
        for path in extracted.rglob("*"):
            if path.is_file() and file_re.fullmatch(path.name):
                selected.append(path)

        if not selected:
            raise SystemExit(
                f"No font file matched {file_re.pattern!r} after extracting "
                f"{len(assets)} asset(s)"
            )

        seen: set[str] = set()
        for path in sorted(selected, key=lambda p: p.name):
            if path.name in seen:
                continue
            seen.add(path.name)
            target = out / path.name
            shutil.copy2(path, target)
            print(f"Selected {target}")

    print(f"Selected {len(seen)} font file(s) for {args.family}")


if __name__ == "__main__":
    main()
