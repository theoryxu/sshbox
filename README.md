# sshbox

Local source repository for the `sshbox` CLI.

## Layout

- `sshbox`: main executable script
- `tests/test_sshbox.py`: CLI regression tests
- `deploy.sh`: publish the repo version to this machine

## Deploy

Default mode copies files into `~/.local/bin`:

```bash
./deploy.sh
```

Use symlinks instead:

```bash
./deploy.sh link
```
