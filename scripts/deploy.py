#!/usr/bin/env python3
"""Update h3yyy's Komodo Compose stack to a release digest, verify, rollback on failure."""
import json
import os
from pathlib import Path
import time
from urllib import error, request

BASE = os.environ["KOMODO_URL"].rstrip("/")
IMAGE = os.environ["IMAGE_REF"]
TAG = os.environ["RELEASE_TAG"]
STACK = "h3yyy"
COMPOSE = Path("compose.yaml").read_text()
HEADERS = {
    "content-type": "application/json",
    "x-api-key": os.environ["KOMODO_API_KEY"],
    "x-api-secret": os.environ["KOMODO_API_SECRET"],
}


def call(path, body):
    req = request.Request(BASE + path, json.dumps(body).encode(), HEADERS, method="POST")
    try:
        with request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except error.HTTPError as exc:
        # Never echo response bodies: they may contain stack configuration or secrets.
        raise RuntimeError(f"Komodo {path} returned HTTP {exc.code}") from exc


def wait(update):
    identifier = update.get("_id")
    if isinstance(identifier, dict):
        identifier = identifier.get("$oid")
    if not identifier:
        raise RuntimeError("Komodo did not return a deployment update ID")
    for _ in range(60):
        result = call("/read/GetUpdate", {"id": identifier})
        if result.get("status") == "Complete":
            if not result.get("success"):
                raise RuntimeError("Komodo deployment failed; inspect its update logs in the UI")
            return
        time.sleep(5)
    raise TimeoutError("Komodo deployment did not finish within five minutes")


def deploy(config):
    call("/write/UpdateStack", {"id": STACK, "config": config})
    wait(call("/execute/DeployStack", {"stack": STACK}))


def verify():
    # This verifies the newly deployed revision, not an old still-running container.
    last_result = "no response"
    for _ in range(30):
        try:
            # Cloudflare rejects Python-urllib's default User-Agent with 403.
            probe = request.Request(
                "https://h3yyy.m3s.app/release.txt",
                headers={"User-Agent": "h3yyy-release-check/1.0"},
            )
            with request.urlopen(probe, timeout=10) as response:
                actual = response.read().decode().strip()
                if actual == TAG:
                    return
                last_result = f"HTTP {response.status}, served {actual!r}"
        except error.HTTPError as exc:
            last_result = f"HTTP {exc.code}"
        except (error.URLError, TimeoutError) as exc:
            last_result = type(exc).__name__
        time.sleep(4)
    raise RuntimeError(f"Public URL did not serve {TAG!r}: {last_result}")


def main():
    if not IMAGE.startswith("ghcr.io/manuelseeger/h3yyy@sha256:"):
        raise ValueError("Expected an immutable h3yyy GHCR digest")
    original = call("/read/GetStack", {"stack": STACK})["config"]
    previous = {"environment": original["environment"], "file_contents": original["file_contents"]}
    desired = {"environment": f"IMAGE_REF={IMAGE}", "file_contents": COMPOSE}
    try:
        deploy(desired)
        verify()
    except Exception:
        if "@sha256:" in previous["environment"]:
            print("Release failed; restoring the prior stack configuration")
            deploy(previous)
        raise
    print(f"Deployed {TAG} ({IMAGE}) to https://h3yyy.m3s.app")


if __name__ == "__main__":
    main()
