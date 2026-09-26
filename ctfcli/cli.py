#!/usr/bin/env python3
"""ctf - ctf-workbench sandbox CLI (zero-dependency, stdlib only).

Entry points:
    python -m ctfcli <cmd> ...
    python ctfcli/cli.py <cmd> ...
    ./ctf <cmd> ...        (Git Bash / Linux wrapper)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

VERSION = "0.1.0"

VALID_TYPES = ["web", "pwn", "crypto", "reverse", "forensics", "ir", "ai", "osint", "misc"]
BUILDABLE_TYPES = ["base", "web", "pwn"]  # MVP: images provided in armory/
IMAGE_PREFIX = "ctf-"
CONTAINER_PREFIX = "ctf-"
NETWORK = "ctf-net"
WORKDIR = "/ctf"


class CtfError(Exception):
    """User-facing error; message is printed and exit code 1 returned."""


def info(msg: str) -> None:
    print(f"[ctf] {msg}")


def ok(msg: str) -> None:
    print(f"[ok] {msg}")


def warn(msg: str) -> None:
    print(f"[!] {msg}", file=sys.stderr)


def die(msg: str) -> None:
    raise CtfError(msg)


# ---------------------------------------------------------------- repo layout

def find_root() -> Path:
    env = os.environ.get("CTF_ROOT")
    if env:
        p = Path(env).expanduser().resolve()
        if (p / "armory").is_dir():
            return p
        die(f"CTF_ROOT={env} does not look like a ctf-workbench repo (no armory/).")
    p = Path.cwd().resolve()
    for d in [p, *p.parents]:
        if (d / "armory").is_dir() and (d / "ctfcli").is_dir():
            return d
    die("not inside a ctf-workbench repo (walked up from cwd, no armory/+ctfcli/ found). "
        "cd into the repo or set CTF_ROOT.")


def ws_dir(root: Path, name: str) -> Path:
    return root / "workspace" / name


def parse_flat_yaml(path: Path) -> dict:
    """Parse the flat 'key: value' subset of YAML used by .ctf.yaml."""
    meta = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#") or ":" not in line:
            continue
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    return meta


def load_meta(root: Path, name: str) -> dict:
    f = ws_dir(root, name) / ".ctf.yaml"
    if not f.is_file():
        die(f"no challenge named '{name}' (missing {f}); list challenges with 'ctf ps'")
    return parse_flat_yaml(f)


def save_meta(root: Path, name: str, meta: dict) -> None:
    f = ws_dir(root, name) / ".ctf.yaml"
    f.write_text("\n".join(f"{k}: {v}" for k, v in meta.items()) + "\n", encoding="utf-8")


def container_of(meta: dict, name: str) -> str:
    return meta.get("container") or (CONTAINER_PREFIX + name)


# ---------------------------------------------------------------- docker helpers

def docker(*args: str, capture: bool = True) -> subprocess.CompletedProcess:
    """Run a docker command. capture=True buffers output; False streams stdio."""
    cmd = ["docker", *args]
    if capture:
        return subprocess.run(cmd, capture_output=True, text=True)
    return subprocess.run(cmd)


def docker_out(*args: str) -> str:
    r = docker(*args)
    if r.returncode != 0:
        raise CtfError((r.stderr or r.stdout or "docker failed").strip())
    return (r.stdout or "").strip()


def image_exists(image: str) -> bool:
    return docker("image", "inspect", image).returncode == 0


def container_status(ctn: str) -> str:
    r = docker("inspect", "-f", "{{.State.Status}}", ctn)
    return r.stdout.strip() if r.returncode == 0 else "missing"


def ensure_network() -> None:
    if docker("network", "inspect", NETWORK).returncode != 0:
        r = docker("network", "create", NETWORK)
        if r.returncode != 0:
            die(f"cannot create docker network '{NETWORK}': {(r.stderr or '').strip()}")
        info(f"created docker network '{NETWORK}'")


# ---------------------------------------------------------------- commands

def notes_template(name: str, ctype: str) -> str:
    return (
        f"# {name}\n\n"
        f"- 方向: {ctype}\n"
        f"- 远程: (未登记, ctf target {name} host:port)\n"
        f"- 状态: 进行中\n\n"
        f"## 过程记录\n\n- \n"
    )


def cmd_init(args) -> int:
    root = find_root()
    name = re.sub(r"[^A-Za-z0-9_.-]+", "-", args.name).strip("-.")
    if not name:
        die(f"invalid challenge name: {args.name!r}")
    if args.type not in VALID_TYPES:
        die(f"--type must be one of: {', '.join(VALID_TYPES)}")
    ws = ws_dir(root, name)
    if ws.exists():
        die(f"workspace already exists: {ws} (pick another name or 'ctf rm {name} --files --yes')")
    image = args.image or IMAGE_PREFIX + args.type
    container = CONTAINER_PREFIX + name

    if not image_exists(image):
        hint = args.type if args.type in BUILDABLE_TYPES else "base"
        die(f"image '{image}' not built yet — run: python -m ctfcli update {hint}")

    (ws / "attachments").mkdir(parents=True)
    (ws / "exploit").mkdir()
    (ws / "notes.md").write_text(notes_template(name, args.type), encoding="utf-8")

    if args.skeleton:
        src = Path(args.skeleton)
        if not src.is_absolute():
            src = root / src
        if not src.is_dir():
            shutil.rmtree(ws, ignore_errors=True)
            die(f"skeleton dir not found: {src}")
        shutil.copytree(src, ws, dirs_exist_ok=True)

    ensure_network()

    publish_args = []
    for p in args.publish or []:
        publish_args += ["-p", f"127.0.0.1:{p}"]
    pwn_args = ["--cap-add=SYS_PTRACE", "--security-opt", "seccomp=unconfined"] \
        if args.type == "pwn" else []

    r = docker(
        "run", "-d", "--name", container, "--hostname", name,
        "--network", NETWORK, *publish_args, *pwn_args,
        "-v", f"{ws.as_posix()}:{WORKDIR}", "-w", WORKDIR,
        image, "tail", "-f", "/dev/null",
    )
    if r.returncode != 0:
        shutil.rmtree(ws, ignore_errors=True)
        die(f"docker run failed: {(r.stderr or r.stdout).strip()}")

    save_meta(root, name, {
        "name": name,
        "type": args.type,
        "image": image,
        "container": container,
        "created": _dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "remote": "",
    })

    ok(f"challenge '{name}' is up")
    print(f"     workspace : workspace/{name}  (mounted at {WORKDIR} in the container)")
    print(f"     container : {container} ({image})")
    if args.skeleton:
        print(f"     skeleton  : {args.skeleton}")
    print("     next      : ctf exec " + name + " <cmd>   |   ctf shell " + name
          + "   |   ctf ps")
    return 0


def cmd_exec(args) -> int:
    root = find_root()
    meta = load_meta(root, args.name)
    ctn = container_of(meta, args.name)
    status = container_status(ctn)
    if status != "running":
        die(f"container {ctn} is '{status}' (not running); check 'ctf ps' or re-init")
    flags = ["-i"] + (["-t"] if sys.stdin.isatty() else [])
    cmd = ["docker", "exec", "-w", WORKDIR, *flags, ctn, *args.cmd]
    try:
        return subprocess.run(cmd).returncode
    except KeyboardInterrupt:
        return 130


def cmd_shell(args) -> int:
    root = find_root()
    meta = load_meta(root, args.name)
    ctn = container_of(meta, args.name)
    if container_status(ctn) != "running":
        die(f"container {ctn} is not running")
    info(f"interactive shell in {ctn} (workdir {WORKDIR}); 'exit' to leave")
    return subprocess.run(["docker", "exec", "-it", "-w", WORKDIR, ctn, "bash"]).returncode


def cmd_stop(args) -> int:
    root = find_root()
    meta = load_meta(root, args.name)
    ctn = container_of(meta, args.name)
    docker("stop", ctn)
    ok(f"stopped {ctn} (workspace kept)")
    return 0


def cmd_rm(args) -> int:
    root = find_root()
    meta = load_meta(root, args.name)
    ctn = container_of(meta, args.name)
    docker("rm", "-f", ctn)
    ok(f"removed container {ctn}")
    ws = ws_dir(root, args.name)
    if args.files:
        if not args.yes:
            if not sys.stdin.isatty():
                die("refusing to delete workspace non-interactively; re-run with --yes")
            answer = input(f"delete workspace {ws} ? [y/N] ").strip().lower()
            if answer not in ("y", "yes"):
                info("workspace kept")
                return 0
        shutil.rmtree(ws, ignore_errors=True)
        ok(f"deleted workspace {ws}")
    else:
        info(f"workspace kept at {ws} (pass --files to delete it too)")
    return 0


def cmd_ps(args) -> int:
    root = find_root()
    wsroot = root / "workspace"
    rows = []
    if wsroot.is_dir():
        for d in sorted(wsroot.iterdir()):
            f = d / ".ctf.yaml"
            if not f.is_file():
                continue
            meta = parse_flat_yaml(f)
            name = meta.get("name") or d.name
            ctn = container_of(meta, name)
            rows.append((name, meta.get("type", "?"), meta.get("image", "?"),
                         ctn, container_status(ctn), meta.get("remote", "") or "-"))
    if not rows:
        info("no challenges yet — start one with: ctf init <name> --type web")
        return 0
    print(f"{'challenge':<20} {'type':<10} {'image':<14} {'container':<24} "
          f"{'state':<10} remote")
    for r in rows:
        print(f"{r[0]:<20} {r[1]:<10} {r[2]:<14} {r[3]:<24} {r[4]:<10} {r[5]}")
    return 0


def cmd_target(args) -> int:
    root = find_root()
    meta = load_meta(root, args.name)
    meta["remote"] = args.hostport
    save_meta(root, args.name, meta)
    ok(f"remote for '{args.name}' -> {args.hostport}")
    return 0


def cmd_doctor(args) -> int:
    try:
        root = find_root()
    except CtfError as e:
        print(f"[x] {e}")
        return 1
    checks = []
    checks.append(("python >= 3.8", sys.version_info >= (3, 8),
                   f"{sys.version.split()[0]} at {sys.executable}"))
    r = docker("--version")
    checks.append(("docker cli", r.returncode == 0, (r.stdout or r.stderr).strip()))
    r = docker("info", "--format", "{{.ServerVersion}}")
    daemon_ok = r.returncode == 0
    checks.append(("docker daemon", daemon_ok,
                   r.stdout.strip() if daemon_ok else "unreachable — start Docker Desktop"))
    r = docker("compose", "version", "--short")
    checks.append(("docker compose", r.returncode == 0,
                   r.stdout.strip() if r.returncode == 0 else "required by 'ctf update'"))
    if daemon_ok:
        for t in BUILDABLE_TYPES:
            img = IMAGE_PREFIX + t
            present = image_exists(img)
            checks.append((f"image {img}", present,
                           "present" if present else f"missing — ctf update {t}"))
        net_ok = docker("network", "inspect", NETWORK).returncode == 0
        checks.append((f"network {NETWORK}", net_ok,
                       "present" if net_ok else "auto-created on first 'ctf init'"))
    usage = shutil.disk_usage(root.anchor)
    free_gb = usage.free / 2**30
    checks.append((f"disk free on {root.anchor}", free_gb > 10, f"{free_gb:.1f} GB"))

    failed = 0
    for name, good, detail in checks:
        mark = "ok  " if good else "FAIL"
        print(f"[{mark}] {name:<24} {detail}")
        if not good:
            failed += 1
    print()
    if failed:
        print(f"doctor: {failed} check(s) failed — fix the [FAIL] items above, "
              f"then re-run 'ctf doctor'")
        return 1
    print("doctor: all checks passed — good to go (start a challenge with 'ctf init')")
    return 0


def cmd_update(args) -> int:
    root = find_root()
    compose = root / "armory" / "docker-compose.yml"
    if not compose.is_file():
        die(f"compose file not found: {compose}")
    targets = list(args.types)
    for t in targets:
        if t not in BUILDABLE_TYPES:
            die(f"cannot build '{t}' (MVP images: {', '.join(BUILDABLE_TYPES)})")
    if "base" not in targets and any(t in ("web", "pwn") for t in targets):
        targets = ["base", *targets]
    for t in targets:
        info(f"building image ctf-{t} ...")
        cmd = ["docker", "compose", "-f", str(compose), "build", t]
        if args.no_cache:
            cmd.append("--no-cache")
        if subprocess.run(cmd).returncode != 0:
            die(f"build failed: {t}")
        ok(f"ctf-{t} ready")
    return 0


# ---------------------------------------------------------------- argparse

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ctf",
        description="ctf-workbench sandbox CLI — per-domain docker sandboxes for CTF work.",
        epilog="Docs: docs/cli.md   |   Design: docs/DESIGN.md",
    )
    p.add_argument("--version", action="version", version=f"ctf {VERSION}")
    sub = p.add_subparsers(dest="command", required=True, metavar="<command>")

    sp = sub.add_parser("init", help="create a challenge workspace and start its sandbox")
    sp.add_argument("name", help="challenge name (a-z0-9_.-)")
    sp.add_argument("--type", required=True, choices=VALID_TYPES, help="challenge domain")
    sp.add_argument("--from", dest="skeleton", metavar="DIR",
                    help="copy a challenge template dir (e.g. examples/web-ssti) into the workspace")
    sp.add_argument("--image", help="override the sandbox image (default: ctf-<type>)")
    sp.add_argument("--publish", action="append", metavar="HOST:CONTAINER",
                    help="publish port to 127.0.0.1, repeatable (e.g. --publish 8080:80)")
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("exec", help="run a command inside the challenge container (main channel)")
    sp.add_argument("name", help="challenge name")
    sp.add_argument("cmd", nargs=argparse.REMAINDER, metavar="CMD...",
                    help="command + args, passed verbatim to the container (no shell)")
    sp.set_defaults(func=cmd_exec)

    sp = sub.add_parser("shell", help="interactive bash in the container (for humans)")
    sp.add_argument("name", help="challenge name")
    sp.set_defaults(func=cmd_shell)

    sp = sub.add_parser("target", help="register the remote target for a challenge")
    sp.add_argument("name", help="challenge name")
    sp.add_argument("hostport", metavar="HOST:PORT", help="e.g. 1.2.3.4:9999")
    sp.set_defaults(func=cmd_target)

    sp = sub.add_parser("stop", help="stop the challenge container")
    sp.add_argument("name", help="challenge name")
    sp.set_defaults(func=cmd_stop)

    sp = sub.add_parser("rm", help="remove the challenge container (workspace kept by default)")
    sp.add_argument("name", help="challenge name")
    sp.add_argument("--files", action="store_true", help="also delete the workspace directory")
    sp.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    sp.set_defaults(func=cmd_rm)

    sub.add_parser("ps", help="list challenges and container states").set_defaults(func=cmd_ps)
    sub.add_parser("doctor", help="environment self-check").set_defaults(func=cmd_doctor)

    sp = sub.add_parser("update", help="build sandbox images (docker compose build)")
    sp.add_argument("types", nargs="+", choices=BUILDABLE_TYPES, metavar="TYPE",
                    help="one or more of: " + ", ".join(BUILDABLE_TYPES))
    sp.add_argument("--no-cache", action="store_true", help="build without cache")
    sp.set_defaults(func=cmd_update)

    return p


def main(argv=None) -> int:
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except CtfError as e:
        print(f"[x] {e}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print("[x] docker not found in PATH — install/start Docker Desktop, "
              "then run 'ctf doctor'", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
