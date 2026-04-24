# Crit Goods — Pack Shot Generator

Fully automated pack-shot generation for all 30 SKUs × 4 angles = **120 images**, using Google's **Gemini 2.5 Flash Image** model (the one everyone calls "nano-banana").

## What this does

For every SKU in the launch catalog, this pipeline generates four product photos in a consistent brand style:

- **front.png** — the hero / e-commerce thumbnail
- **flatlay.png** — top-down editorial shot with soft props
- **detail.png** — macro close-up of material + print quality
- **on_body.png** — lifestyle / on-model / in-context shot

Every image is composed from three layers:

1. A **style base** that locks the Crit Goods visual system (Bone / Void / Ash / Crit Red) into every frame.
2. An **angle template** that controls camera, composition, and lighting.
3. A **per-SKU design description** pulled from `pack_shots_prompts.json` — 30 individually written design briefs.

The Python script assembles them, calls Gemini in parallel, and drops the PNGs into the right folders.

## Setup (one time)

```bash
# 1. From the Video Game Merch folder:
pip install -r requirements.txt

# 2. Get a Gemini API key at https://aistudio.google.com/apikey, then:
export GEMINI_API_KEY="paste-your-key-here"
```

Requires Python 3.9+.

## Run

```bash
# Default: generate everything, 4 workers in parallel
python generate_pack_shots.py

# Preview without spending any API credits:
python generate_pack_shots.py --dry-run

# Just regenerate one SKU:
python generate_pack_shots.py --sku CG-HD2-001

# Just regenerate one angle across every SKU:
python generate_pack_shots.py --angle front

# Use more workers for a faster full run:
python generate_pack_shots.py --workers 8

# Force re-generation even if a PNG already exists:
python generate_pack_shots.py --force
```

### Output

```
pack-shots/
├── manifest.json               # status + timing for every job
├── hades-ii/
│   ├── CG-HD2-001/
│   │   ├── front.png
│   │   ├── flatlay.png
│   │   ├── detail.png
│   │   └── on_body.png
│   ├── CG-HD2-002/ ...
│   └── ...
├── elden-ring-sote/
├── baldurs-gate-3/
├── zelda-totk/
├── zelda-classic/
├── street-fighter-6/
├── street-fighter-classic/
├── mortal-kombat-1/
├── mortal-kombat-classic/
├── helldivers-2/
├── black-myth-wukong/
├── final-fantasy-vii-rebirth/
├── metaphor-refantazio/
└── monster-hunter-wilds/
```

## Resumability

Already-generated PNGs are skipped automatically. If a job fails mid-run, just re-run the same command — it will only regenerate the missing ones. Use `--force` to overwrite.

## Cost & runtime estimate

- **Model:** `gemini-2.5-flash-image-preview` (nano-banana)
- **Cost at time of writing:** ~$0.039 / image → **~$4.68** for a full 120-image run. Confirm in Google AI Studio before running.
- **Runtime:** ~6–12 minutes on 4 workers depending on API latency.

## Tweaking the look

All creative direction lives in **`pack_shots_prompts.json`**. Edit:

- `style_base` — global look (color palette, vibe, quality bar)
- `angle_templates` — camera, composition, lighting per angle
- `product_material_specs` — fabric / paper / metal specs per category
- `skus[*].design` — the design of the specific SKU's art / print
- `skus[*].on_body_variant` — the lifestyle / model shot direction

Change any of these, re-run with `--force` (or delete the PNGs you want regenerated), and the new aesthetic propagates across every SKU.

## Extending

- **New SKU:** add an object to `skus` in the JSON, re-run.
- **New angle:** add a key to `angle_templates` and to the `ANGLES` list at the top of `generate_pack_shots.py`.
- **Swap providers:** replace the body of `generate_one()` with a call to whatever image API you prefer (Replicate, OpenAI `gpt-image-1`, Stability, etc.). The job enumeration + folder layout + resumability all stay.

## Troubleshooting

- **`google-genai` missing** → `pip install -r requirements.txt`
- **`GEMINI_API_KEY is not set`** → `export GEMINI_API_KEY="..."`
- **`No image bytes returned`** → the prompt may have tripped a safety filter (some on-body prompts can). Re-run with `--force --sku <sku> --angle on_body` and nudge the `on_body_variant` in the JSON.
- **Rate-limit errors** → lower `--workers` (try 2 or 3).
