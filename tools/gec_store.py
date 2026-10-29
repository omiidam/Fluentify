#!/usr/bin/env python3
"""Put the GEC-BART Base checkpoint in ArvanCloud object storage, and get it back.

    python3 tools/gec_store.py --check
    python3 tools/gec_store.py --manifest            # checksums for what is local
    python3 tools/gec_store.py --upload
    python3 tools/gec_store.py --verify
    python3 tools/gec_store.py --download            # into the cache the server reads

Object storage is a place to keep the files. It does not run the model: BART
needs torch, so the Python service loads the checkpoint from its own disk and
only calls this tool on install, cache recovery or a version change.

Location and identity come from gec.json (`storage`), never from this file:

    endpoint  https://s3.ir-thr-at1.arvanstorage.ir
    region    ir-thr-at1
    bucket    fluentify-bbc            (private)
    prefix    "GEC-BART BASE/"

Credentials come from the environment, or from `.arvan-storage.env` beside the
project (gitignored), and are never printed:

    ARVAN_S3_ENDPOINT=            ARVAN_S3_ACCESS_KEY_ID=
    ARVAN_S3_REGION=ir-thr-at1    ARVAN_S3_SECRET_ACCESS_KEY=
    ARVAN_S3_BUCKET=fluentify-bbc
    ARVAN_S3_PREFIX=GEC-BART BASE/

Every upload is verified twice - size and SHA-256 read back from the object's
metadata - because a truncated 558 MB upload that reports success is exactly
the failure that only shows up when the model will not load. The bucket is
never made public and nothing outside the prefix is touched.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "gec.json"

KINDS = {".safetensors": "application/octet-stream",
         ".json": "application/json",
         ".txt": "text/plain",
         ".md": "text/markdown"}

ENV_NAMES = ("ARVAN_S3_ENDPOINT", "ARVAN_S3_REGION", "ARVAN_S3_BUCKET",
             "ARVAN_S3_PREFIX", "ARVAN_S3_ACCESS_KEY_ID",
             "ARVAN_S3_SECRET_ACCESS_KEY")


# --------------------------------------------------------------------------
# settings
# --------------------------------------------------------------------------
def load_config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}


def read_env_file(path: Path) -> dict:
    """KEY=VALUE lines, comments and blanks skipped. Values are never printed."""
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def settings(cfg: dict | None = None) -> dict:
    """The storage location from gec.json, credentials from the environment."""
    cfg = cfg or load_config()
    store = cfg.get("storage", {})
    env_file = ROOT / store.get("env_file", ".arvan-storage.env")
    file_env = read_env_file(env_file)
    pick = lambda name, default="": os.environ.get(name) or file_env.get(name) or default
    return {
        "endpoint": pick("ARVAN_S3_ENDPOINT", store.get("endpoint", "")),
        "region": pick("ARVAN_S3_REGION", store.get("region", "ir-thr-at1")),
        "bucket": pick("ARVAN_S3_BUCKET", store.get("bucket", "")),
        "prefix": pick("ARVAN_S3_PREFIX", store.get("prefix", "")),
        "key": pick("ARVAN_S3_ACCESS_KEY_ID"),
        "secret": pick("ARVAN_S3_SECRET_ACCESS_KEY"),
        "manifest": store.get("manifest", "manifest.json"),
    }


def missing_credentials(s: dict) -> list[str]:
    return [name for name, value in
            (("ARVAN_S3_ACCESS_KEY_ID", s["key"]),
             ("ARVAN_S3_SECRET_ACCESS_KEY", s["secret"]))
            if not value]


def client(s: dict):
    """An S3 client for ArvanCloud, or a RuntimeError naming what is missing."""
    absent = missing_credentials(s)
    if absent:
        raise RuntimeError(
            "no ArvanCloud credentials: set " + " and ".join(absent) +
            " in the environment or in .arvan-storage.env (both gitignored).\n"
            "  The console URL is not the S3 endpoint; the endpoint is " +
            (s["endpoint"] or "in gec.json → storage.endpoint"))
    import boto3
    from botocore.config import Config

    return boto3.client(
        "s3",
        endpoint_url=s["endpoint"],
        region_name=s["region"],
        aws_access_key_id=s["key"],
        aws_secret_access_key=s["secret"],
        config=Config(signature_version="s3v4", retries={"max_attempts": 5,
                                                         "mode": "standard"}),
    )


# --------------------------------------------------------------------------
# manifests
# --------------------------------------------------------------------------
def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def local_files(cfg: dict, model_dir: Path) -> list[Path]:
    return [model_dir / name for name in cfg["model"]["files"]]


def build_manifest(cfg: dict, model_dir: Path) -> dict:
    """Identity plus a checksum per file: what the server checks before loading."""
    model = cfg["model"]
    rows = []
    for path in local_files(cfg, model_dir):
        if not path.exists():
            raise RuntimeError(f"{path.name} is not in {model_dir}")
        rows.append({"name": path.name, "bytes": path.stat().st_size,
                     "sha256": sha256(path)})
    attribution = model_dir / model.get("attribution", "README.md")
    if attribution.exists():
        rows.append({"name": attribution.name, "bytes": attribution.stat().st_size,
                     "sha256": sha256(attribution)})
    return {
        "_readme": "Written by tools/gec_store.py. The Python service verifies "
                   "these checksums before it loads the model.",
        "model": model["id"],
        "revision": model["revision"],
        "license": model.get("license", ""),
        "architecture": model.get("architecture", ""),
        "files": rows,
        "total_bytes": sum(r["bytes"] for r in rows),
        "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def read_manifest(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def key_for(s: dict, name: str) -> str:
    prefix = s["prefix"]
    return f"{prefix}{name}"


# --------------------------------------------------------------------------
# upload / download / verify
# --------------------------------------------------------------------------
def upload(cfg: dict, model_dir: Path, dry_run: bool = False) -> int:
    s = settings(cfg)
    manifest = build_manifest(cfg, model_dir)
    rows = manifest["files"]
    print(f"model     {manifest['model']} @ {manifest['revision']}")
    print(f"target    s3://{s['bucket']}/{s['prefix']}")
    print(f"files     {len(rows)} · {manifest['total_bytes'] / 1048576:.1f} MB")
    if dry_run:
        for row in rows:
            print(f"  would upload {row['name']:<24} {row['bytes']:>10}  {row['sha256'][:16]}")
        return 0

    s3 = client(s)
    # The bucket has to exist and be ours before anything else; a typo in the
    # bucket name should fail here, not after 558 MB.
    try:
        s3.head_bucket(Bucket=s["bucket"])
    except Exception as exc:
        print(f"FAIL  bucket {s['bucket']!r} is not reachable: {exc}", file=sys.stderr)
        return 1

    for row in rows:
        path = model_dir / row["name"]
        key = key_for(s, row["name"])
        s3.upload_file(
            str(path), s["bucket"], key,
            ExtraArgs={"ContentType": KINDS.get(path.suffix, "application/octet-stream"),
                       "Metadata": {"sha256": row["sha256"],
                                    "model": manifest["model"],
                                    "revision": manifest["revision"]}},
        )
        head = s3.head_object(Bucket=s["bucket"], Key=key)
        remote_sha = (head.get("Metadata") or {}).get("sha256", "")
        ok = head["ContentLength"] == row["bytes"] and remote_sha == row["sha256"]
        print(f"  {'ok  ' if ok else 'FAIL'} {row['name']:<24} "
              f"{head['ContentLength']:>10}  {remote_sha[:16]}")
        if not ok:
            print("FAIL  the object read back does not match what was uploaded",
                  file=sys.stderr)
            return 1

    body = json.dumps(manifest, indent=1).encode("utf-8")
    s3.put_object(Bucket=s["bucket"], Key=key_for(s, s["manifest"]), Body=body,
                  ContentType="application/json")
    print(f"  ok   {s['manifest']:<24} {len(body):>10}  (identity + checksums)")
    print(f"PASS  {len(rows)} files verified in s3://{s['bucket']}/{s['prefix']}")
    return 0


def download(cfg: dict, dest: Path) -> int:
    """Fetch what is missing, verify it, and write the manifest beside it."""
    s = settings(cfg)
    dest.mkdir(parents=True, exist_ok=True)
    s3 = client(s)
    remote = None
    try:
        obj = s3.get_object(Bucket=s["bucket"], Key=key_for(s, s["manifest"]))
        remote = json.loads(obj["Body"].read())
    except Exception:
        pass
    if remote and remote.get("revision") and remote["revision"] != cfg["model"]["revision"]:
        print(f"FAIL  the bucket holds revision {remote['revision']}, gec.json pins "
              f"{cfg['model']['revision']}", file=sys.stderr)
        return 1

    wanted = {row["name"]: row for row in
              (remote or {}).get("files", [])} or {
        name: {"name": name} for name in cfg["model"]["files"]}
    for name, row in wanted.items():
        path = dest / name
        if path.exists() and (not row.get("bytes") or
                              path.stat().st_size == row["bytes"]):
            print(f"  have {name}")
            continue
        print(f"  get  {name}")
        s3.download_file(s["bucket"], key_for(s, name), str(path))
        got = path.stat().st_size
        if row.get("bytes") and got != row["bytes"]:
            print(f"FAIL  {name} is {got} bytes, the manifest says {row['bytes']}",
                  file=sys.stderr)
            return 1
        if row.get("sha256") and sha256(path) != row["sha256"]:
            print(f"FAIL  {name} does not match its checksum", file=sys.stderr)
            return 1

    manifest = remote or build_manifest_from_dir(cfg, dest)
    (dest / s["manifest"]).write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"PASS  {len(wanted)} files in {dest}")
    return 0


def build_manifest_from_dir(cfg: dict, dest: Path) -> dict:
    """A manifest for a cache that arrived without one (local install)."""
    rows = []
    for name in cfg["model"]["files"]:
        path = dest / name
        if path.exists():
            rows.append({"name": name, "bytes": path.stat().st_size,
                         "sha256": sha256(path)})
    return {"model": cfg["model"]["id"], "revision": cfg["model"]["revision"],
            "license": cfg["model"].get("license", ""), "files": rows,
            "total_bytes": sum(r["bytes"] for r in rows)}


def verify(cfg: dict, model_dir: Path) -> int:
    s = settings(cfg)
    local = build_manifest(cfg, model_dir)
    try:
        s3 = client(s)
        obj = s3.get_object(Bucket=s["bucket"], Key=key_for(s, s["manifest"]))
        remote = json.loads(obj["Body"].read())
    except RuntimeError as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"FAIL  no manifest at s3://{s['bucket']}/{key_for(s, s['manifest'])}: {exc}",
              file=sys.stderr)
        return 1

    problems = []
    if remote.get("revision") != local.get("revision"):
        problems.append(f"revision {remote.get('revision')} != {local.get('revision')}")
    by_name = {row["name"]: row for row in remote.get("files", [])}
    for row in local["files"]:
        other = by_name.get(row["name"])
        if not other:
            problems.append(f"{row['name']} is not in the bucket")
        elif other.get("sha256") != row["sha256"]:
            problems.append(f"{row['name']} checksum differs")
    for message in problems:
        print(f"FAIL  {message}")
    if problems:
        return 1
    print(f"PASS  local {len(local['files'])} files match s3://{s['bucket']}/{s['prefix']}")
    return 0


def check(cfg: dict) -> int:
    s = settings(cfg)
    print("ArvanCloud object storage for the GEC-BART Base checkpoint")
    print(f"  endpoint  {s['endpoint'] or '(not set)'}")
    print(f"  region    {s['region']}")
    print(f"  bucket    {s['bucket']}  (private; the model is fetched with these keys)")
    print(f"  prefix    {s['prefix']!r}")
    print(f"  manifest  {s['manifest']}")
    absent = missing_credentials(s)
    print(f"  keys      {'missing: ' + ', '.join(absent) if absent else 'present'}")
    if absent:
        print("\n  Add them to .arvan-storage.env (gitignored) or the environment:\n"
              "    ARVAN_S3_ACCESS_KEY_ID=…\n    ARVAN_S3_SECRET_ACCESS_KEY=…")
        return 1
    s3 = client(s)
    try:
        s3.head_bucket(Bucket=s["bucket"])
    except Exception as exc:
        print(f"\n  FAIL  bucket is not reachable: {exc}")
        return 1
    listing = s3.list_objects_v2(Bucket=s["bucket"], Prefix=s["prefix"])
    objects = listing.get("Contents", [])
    print(f"  objects   {len(objects)} under the prefix")
    for obj in objects:
        print(f"    {obj['Key'].split('/')[-1]:<24} {obj['Size']:>10}")
    print("  PASS  credentials work and the bucket is reachable")
    return 0


# --------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    cfg = load_config()
    cache = Path(os.environ.get(cfg.get("env", {}).get("model_dir", "FLUENTIFY_GEC_DIR"), "")
                 or ROOT / cfg["run"]["cache_dir"])
    parser = argparse.ArgumentParser(
        description="Upload, fetch or verify the GEC-BART Base checkpoint.")
    parser.add_argument("--check", action="store_true",
                        help="credentials, bucket and prefix, listing what is there")
    parser.add_argument("--manifest", action="store_true",
                        help="checksums for the local checkpoint, printed only")
    parser.add_argument("--upload", action="store_true", help="upload and verify")
    parser.add_argument("--download", action="store_true",
                        help="fetch missing files into the cache and verify them")
    parser.add_argument("--verify", action="store_true",
                        help="compare the local cache with the bucket's manifest")
    parser.add_argument("--dry-run", action="store_true", help="with --upload: list only")
    parser.add_argument("--dir", help="model directory (default: the configured cache)")
    args = parser.parse_args(argv)

    model_dir = Path(args.dir) if args.dir else cache
    if args.check:
        return check(cfg)
    if args.manifest:
        print(json.dumps(build_manifest(cfg, model_dir), indent=1))
        return 0
    if args.upload:
        return upload(cfg, model_dir, dry_run=args.dry_run)
    if args.download:
        return download(cfg, model_dir)
    if args.verify:
        return verify(cfg, model_dir)
    parser.print_help()
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        raise SystemExit(3)
    except KeyboardInterrupt:
        raise SystemExit(130)
