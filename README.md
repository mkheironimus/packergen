# packergen
Generate JSON files for Packer (http://packer.io/) from human-friendly YAML
sources.

Current implementations are prototype-quality and lack any reasonable error
checking or documentation.

## perl6

Perl 6 (rakudo-star) implementation, plus a Dockerfile to build an image that
can run it.

It requires the `JSON::Pretty` and `YAMLish` modules, both available through
panda.

## python

Python 2.7 implementation. It uses argparse which is documented as being new in
2.7, so older releases are unlikely to work.

## sample

Example YAML source files to build CentOS 6 and 7 images.
