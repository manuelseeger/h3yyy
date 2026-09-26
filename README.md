# h3yyy

A small Compose-deployed application at <https://h3yyy.m3s.app>.

## Releases

Publish a non-prerelease GitHub release from a tag on `main`. The release workflow builds the tagged Dockerfile, pushes it to GHCR, updates the `h3yyy` Komodo stack with the immutable image digest and this repo's `compose.yaml`, then verifies `/release.txt` on the public URL. If verification fails, it restores the previous Compose configuration and digest. Deployments and container logs are visible in Komodo at `http://100.105.6.60:9120` from the tailnet.

This public proof repo uses the `p` environment secrets `KOMODO_API_KEY` and `KOMODO_API_SECRET`, and non-secret environment variables `TS_OIDC_CLIENT_ID` and `TS_OIDC_AUDIENCE`. For future **private** repos on a personal GitHub Free account, use repository secrets and variables instead (private environment secrets require Pro). GitHub Pro does not share secrets across personal repositories. The Komodo API key must be restricted to this stack with Write permission. Protect releases/tags against untrusted collaborators: Write access to a Komodo Compose stack can run arbitrary containers on gail and is effectively host-root access.

### Tailscale identity (no shared credential in GitHub)

In the Tailscale admin console, create an **OpenID Connect federated trust credential** (not an OAuth client secret): issuer `GitHub Actions` / `https://token.actions.githubusercontent.com`, subject `repo:manuelseeger@45933060/h3yyy@1388727020:environment:p` (this repo uses GitHub's post-July-2026 immutable subject format). Optionally match custom claims `repository_id = 1388727020` and `event_name = release`. Grant only `auth_keys` write scope for `tag:github-actions`. Permit that tag to access gail on TCP 9120 in tailnet policy. Copy the returned **client ID** and **audience** (neither is a secret) into the GitHub `p` environment variables `TS_OIDC_CLIENT_ID` and `TS_OIDC_AUDIENCE`. The release job has `id-token: write`; Tailscale joins the runner as an ephemeral tagged device after checking the GitHub-signed OIDC token. No long-lived Tailscale secret is stored in this repo.

GHCR package visibility must permit gail to pull the image. For a public package, anonymous pulls work; a private package requires registry credentials in Komodo. Do not expose Komodo through the public wildcard Caddy ingress.

Local Compose validation:

```sh
IMAGE_REF=ghcr.io/manuelseeger/h3yyy@sha256:$(printf 'a%.0s' {1..64}) docker compose config --quiet
```
