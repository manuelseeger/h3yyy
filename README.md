# h3yyy

A small Compose-deployed application at <https://h3yyy.m3s.app>.

## Releases

Publish a non-prerelease GitHub release from a tag on `main`. The release workflow builds the tagged Dockerfile, pushes it to GHCR, updates the `h3yyy` Komodo stack with the immutable image digest and this repo's `compose.yaml`, then verifies `/release.txt` on the public URL. If verification fails, it restores the previous Compose configuration and digest. Deployments and container logs are visible in Komodo at `http://100.105.6.60:9120` from the tailnet.

The `production` environment needs `TS_OAUTH_CLIENT_ID`, `TS_OAUTH_SECRET`, `KOMODO_API_KEY`, and `KOMODO_API_SECRET` secrets. The Tailscale OAuth client must be allowed to advertise `tag:github-actions`; tailnet policy must allow that tag to connect to gail on TCP 9120. The Komodo API key must be restricted to this stack, with Write and Execute permissions. Protect releases/tags against untrusted collaborators: Write access to a Komodo Compose stack can run arbitrary containers on gail and is effectively host-root access.

GHCR package visibility must permit gail to pull the image. For a public package, anonymous pulls work; a private package requires registry credentials in Komodo. Do not expose Komodo through the public wildcard Caddy ingress.

Local Compose validation:

```sh
IMAGE_REF=ghcr.io/manuelseeger/h3yyy@sha256:$(printf 'a%.0s' {1..64}) docker compose config --quiet
```
