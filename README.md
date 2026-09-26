# h3yyy

A small public HTTP demo intended for <https://h3yyy.m3s.app>.

The root `compose.yaml` is ordinary Compose: one locally built nginx service, a normal `/healthz` endpoint and a container healthcheck. It does not publish a host port; the m3s controller assigns a loopback-only port to the registered entry service and Caddy handles HTTPS. The app does not need a release marker, registry image, deployment workflow or deployment secret.

## Local smoke test

```sh
docker compose -f compose.yaml -f compose.dev.yaml up --build --wait -d
curl --fail http://127.0.0.1:18080/
curl --fail http://127.0.0.1:18080/healthz
docker compose -f compose.yaml -f compose.dev.yaml down --remove-orphans
```

`compose.dev.yaml` is only for local development; production reads the root `compose.yaml` alone.

## Releases

After registration in the trusted m3s registry (`repository: manuelseeger/h3yyy`, chosen `slug`, `service: web`, `port: 80`, `health_path: /healthz`), publish a non-draft, non-prerelease GitHub release at a new tag. The m3s controller polls releases, resolves the tag to a commit, builds the source and deploys it. CI only tests the app; it does not deploy. No app-specific credentials, DNS edit or infrastructure change is needed for later releases. A slug rename is a registry change, not a new app identity. Do not move a published tag. Access to release publishing and Dockerfile editing is trusted host-code access.

For a visible update, change `index.html` in a new commit and publish another release. The homepage is human-facing content, not a deployment verification protocol. The platform checks the normal health endpoint and container healthcheck.
