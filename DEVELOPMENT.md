# macdump Development Hints

## Versioning

Semantic versioning ([semver](https://semver.org/)) is used.
The tool [bumpver](https://github.com/mbarkhau/bumpver) keeps versions
consistent across files.
To bump the version, use a command like this: `bumpver update --patch --dry` to
see what would change, and leave `--dry` out to actually do it.
