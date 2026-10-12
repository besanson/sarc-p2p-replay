# data/

Empty in the repository. `make bootstrap` (or `make fetch-data`) downloads the
registered event logs here from 4TU.ResearchData and checks each file against
the SHA-256 committed in `prereg/data.lock` and `prereg/p7-v1.md` section Data.
A file whose hash does not match is deleted and the target fails.

Nothing in this directory except this note is committed.
