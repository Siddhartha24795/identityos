# This is a frozen snapshot

This folder is an immutable copy of IdentityOS **v1**, taken from the live
working directory at `../identityos/` once v1 was complete and verified.

- Ongoing development continues in `../identityos/` (the live directory).
- When v2 is complete, it will be snapshotted the same way into
  `../identityos-v2/`.
- No `.venv`, `.git`, or cache directories were copied — this snapshot is
  meant to be reproducible standalone via `make setup` from a clean
  environment, same as the live directory.

See `README.md` for everything else.
