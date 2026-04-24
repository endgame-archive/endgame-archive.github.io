#!/usr/bin/env python3
"""
Crit Goods — Pack Shot Generator
================================

Generates product pack shots for every SKU × angle using Google's
Gemini 2.5 Flash Image ("nano-banana") model, in parallel, with resumability.

Usage
-----
  1. pip install -r requirements.txt
  2. export GEMINI_API_KEY="<your key>"         # or set GOOGLE_API_KEY
  3. python generate_pack_shots.py              # generate everything
     python generate_pack_shots.py --dry-run    # just print prompts, no API calls
     python generate_pack_shots.py --sku CG-HD2-001   # one SKU only
     python generate_pack_shots.py --angle front      # one angle across all SKUs
     python generate_pack_shots.py --workers 8        # more parallel workers
     python generate_pack_shots.py --force            # re-generate even if file exists

Output
------
  pack-shots/<game-slug>/<SKU>/front.png
                              /flatlay.png
                              /detail.png
                              /on_body.png
  pack-shots/manifest.json    (written after each run)

Notes
-----
• Resumable: by default, any existing PNG is skipped. Delete files or pass
  --force to re-generate.
• Model: gemini-2.5-flash-image-preview (aka "nano-banana"). Override with
  --model to try a different one.
• Cost at time of writing: ~$0.039 per image for gemini-2.5-flash-image-preview,
  so ~$4.68 for a full run of 120 images. Check current pricing in Google AI
  Studio before a large batch.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

# ---------- config ----------
HERE = Path(__file__).resolve().parent
PROMPTS_PATH = HERE / "pack_shots_prompts.json"
OUTPUT_ROOT = HERE / "pack-shots"
MANIFEST_PATH = OUTPUT_ROOT / "manifest.json"

ANGLES = ["front", "flatlay", "detail", "on_body"]
DEFAULT_MODEL = "gemini-2.5-flash-image-preview"

# ---------- data classes ----------
@dataclass
class Job:
    sku: str
    game: str
    game_slug: str
    category: str
    title: str
    angle: str
    prompt: str
    out_path: Path


@dataclass
class Result:
    sku: str
    angle: str
    out_path: str
    status: str            # "ok", "skipped", "error", "dry_run"
    duration_s: float
    error: Optional[str] = None


# ---------- prompt assembly ----------
def build_prompt(prompts: dict, sku: dict, angle: str) -> str:
    """Compose the final text prompt by layering style_base + angle + SKU specifics."""
    style_base = prompts["style_base"]
    angle_template = prompts["angle_templates"][angle]
    material = prompts["product_material_specs"].get(sku["category"], "")

    # On-body needs the SKU-specific variant note
    extra = ""
    if angle == "on_body":
        extra = "\n\nProduct-specific on-body direction:\n" + sku.get("on_body_variant", "")

    return (
        f"{style_base}\n\n"
        f"PRODUCT: {sku['title']} — a {sku['category'].lower()} for the game '{sku['game']}' (SKU {sku['sku']}).\n\n"
        f"MATERIAL / CONSTRUCTION: {material}\n\n"
        f"DESIGN: {sku['design']}\n\n"
        f"CAMERA & COMPOSITION: {angle_template}{extra}\n\n"
        f"Final output: one square 1024x1024 image, sharp, true-to-life, no text watermarks, "
        f"no visible real-world trademarks or other brand names."
    )


def enumerate_jobs(prompts: dict, filter_sku: Optional[str], filter_angle: Optional[str]) -> list[Job]:
    jobs: list[Job] = []
    for sku in prompts["skus"]:
        if filter_sku and sku["sku"] != filter_sku:
            continue
        out_dir = OUTPUT_ROOT / sku["game_slug"] / sku["sku"]
        out_dir.mkdir(parents=True, exist_ok=True)
        for angle in ANGLES:
            if filter_angle and angle != filter_angle:
                continue
            jobs.append(Job(
                sku=sku["sku"],
                game=sku["game"],
                game_slug=sku["game_slug"],
                category=sku["category"],
                title=sku["title"],
                angle=angle,
                prompt=build_prompt(prompts, sku, angle),
                out_path=out_dir / f"{angle}.png",
            ))
    return jobs


# ---------- Gemini call ----------
def _lazy_import_genai():
    try:
        from google import genai  # type: ignore
        from google.genai import types  # type: ignore
        return genai, types
    except ImportError:
        sys.exit(
            "Missing dependency: google-genai.\n"
            "Install it with:  pip install google-genai\n"
            "(or: pip install -r requirements.txt)"
        )


def get_client():
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        sys.exit(
            "GEMINI_API_KEY (or GOOGLE_API_KEY) env var is not set.\n"
            "Get a key at https://aistudio.google.com/apikey, then:\n"
            "  export GEMINI_API_KEY='...'"
        )
    genai, _ = _lazy_import_genai()
    return genai.Client(api_key=key)


def generate_one(client, model: str, job: Job, max_retries: int = 3) -> Result:
    """Call Gemini, save first image part returned to job.out_path."""
    genai, types = _lazy_import_genai()

    start = time.time()
    last_err: Optional[str] = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = client.models.generate_content(
                model=model,
                contents=[job.prompt],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )
            # Walk response for the first image part
            image_bytes: Optional[bytes] = None
            for candidate in (resp.candidates or []):
                for part in (candidate.content.parts or []):
                    inline = getattr(part, "inline_data", None)
                    if inline and getattr(inline, "data", None):
                        data = inline.data
                        image_bytes = data if isinstance(data, (bytes, bytearray)) else base64.b64decode(data)
                        break
                if image_bytes:
                    break
            if not image_bytes:
                raise RuntimeError("No image bytes returned by the model")
            job.out_path.write_bytes(image_bytes)
            return Result(job.sku, job.angle, str(job.out_path), "ok", round(time.time() - start, 2))
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            if attempt < max_retries:
                time.sleep(1.5 ** attempt)  # simple backoff
    return Result(job.sku, job.angle, str(job.out_path), "error", round(time.time() - start, 2), last_err)


# ---------- runner ----------
def run(args):
    prompts = json.loads(PROMPTS_PATH.read_text())
    jobs = enumerate_jobs(prompts, args.sku, args.angle)

    # Filter out jobs whose output already exists (unless --force)
    pending: list[Job] = []
    skipped: list[Result] = []
    for job in jobs:
        if job.out_path.exists() and not args.force:
            skipped.append(Result(job.sku, job.angle, str(job.out_path), "skipped", 0.0))
        else:
            pending.append(job)

    print(f"Total jobs:   {len(jobs)}")
    print(f"Already done: {len(skipped)}")
    print(f"Pending:      {len(pending)}")
    print()

    if args.dry_run:
        for j in pending[: args.limit_preview]:
            print(f"— {j.sku} / {j.angle}  →  {j.out_path.relative_to(HERE)}")
            print(j.prompt[:400] + ("…" if len(j.prompt) > 400 else ""))
            print()
        more = len(pending) - args.limit_preview
        if more > 0:
            print(f"(… {more} more prompts not shown. Remove --dry-run to generate.)")
        _write_manifest(jobs, skipped, dry_run=True)
        return 0

    if not pending:
        print("Nothing to do. Pass --force to re-generate existing files.")
        _write_manifest(jobs, skipped)
        return 0

    client = get_client()
    model = args.model

    print(f"Generating {len(pending)} images with {model} using {args.workers} workers…\n")
    results: list[Result] = list(skipped)
    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(generate_one, client, model, j): j for j in pending}
        for fut in as_completed(futures):
            r = fut.result()
            results.append(r)
            done += 1
            tag = {"ok": "✓", "error": "✗", "skipped": "·"}.get(r.status, "?")
            rel = Path(r.out_path).relative_to(HERE)
            msg = f"[{done}/{len(pending)}] {tag} {r.sku} {r.angle:<8} {r.duration_s:>5.2f}s  {rel}"
            if r.error:
                msg += f"  ← {r.error}"
            print(msg)

    _write_manifest(jobs, results)
    oks = sum(1 for r in results if r.status == "ok")
    errs = sum(1 for r in results if r.status == "error")
    print(f"\nDone. {oks} generated, {errs} errors, {len(skipped)} skipped.")
    print(f"Manifest: {MANIFEST_PATH.relative_to(HERE)}")
    if errs:
        print("Re-run the command to retry the failed jobs (successful ones are cached).")
        return 1
    return 0


def _write_manifest(all_jobs: list[Job], results: list[Result], dry_run: bool = False) -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    data = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "dry_run": dry_run,
        "total_jobs": len(all_jobs),
        "results": [asdict(r) for r in results],
    }
    MANIFEST_PATH.write_text(json.dumps(data, indent=2))


def parse_args():
    p = argparse.ArgumentParser(
        description="Generate Crit Goods pack shots with Gemini 2.5 Flash Image.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--dry-run", action="store_true", help="Print prompts + planned paths without calling the API.")
    p.add_argument("--sku", help="Run one SKU only (e.g. CG-HD2-001).")
    p.add_argument("--angle", choices=ANGLES, help="Run one angle across all SKUs.")
    p.add_argument("--workers", type=int, default=4, help="Parallel workers.")
    p.add_argument("--model", default=DEFAULT_MODEL, help="Gemini image model.")
    p.add_argument("--force", action="store_true", help="Overwrite existing PNGs.")
    p.add_argument("--limit-preview", type=int, default=3, help="Max prompts printed in --dry-run.")
    return p.parse_args()


if __name__ == "__main__":
    sys.exit(run(parse_args()))
