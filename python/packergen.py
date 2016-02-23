#! /usr/bin/python

import argparse
import json
import sys
import yaml

def load_yaml(name):
    """Utility function to import a YAML file."""
    y = open(name, 'r')
    yml = yaml.safe_load(y)
    y.close()
    return yml


def expand_entry(entry):
    """Load all of the templates in an entry."""
    new = {}
    if 'config_template' in entry:
        if type(entry['config_template']).__name__ == 'str':
            new.update(load_yaml(entry['config_template']))
        else:
            [new.update(load_yaml(tmpl)) for tmpl in entry['config_template']]
        del entry['config_template']
    new.update(entry)
    return new


def build(name, builder):
    """Process and return a single builder."""
    b = expand_entry(builder)
    b['name'] = name
    return b


def provision(prov, cfg):
    """Process and return a single provisioner."""
    p = expand_entry(prov)
    if 'provisioner_override' in cfg and not 'override' in prov:
        p['override'] = cfg['provisioner_override']
    return p


def postproc(post):
    """Process and return a postprocessor entry, which can be either a single
    postprocessor or a group (array) of postprocessors."""
    return expand_entry(post) if type(post).__name__ == 'dict' else [
            expand_entry(p) for p in post ]


def generate_packer(cfg):
    pack = { 'builders': [] }
    for name, builder in cfg['builders'].iteritems():
        pack['builders'].append(build(name, builder))

    if 'provisioners' in cfg:
        pack['provisioners'] = [provision(p, cfg) for p in cfg['provisioners']]

    if 'post-processors' in cfg:
        pack['post-processors'] = [postproc(p) for p in cfg['post-processors']]

    if 'description' in cfg:
        pack['description'] = cfg['description']

    if 'variables' in cfg:
        pack['variables'] = cfg['variables']

    return pack


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Generate Packer configuration from YAML')
    parser.add_argument('--in', dest='src', nargs='?',
            type=argparse.FileType('r'), default=sys.stdin,
            help='input YAML file', metavar='file.yml')
    parser.add_argument('--out', dest='dest', nargs='?',
            type=argparse.FileType('w'), default=sys.stdout,
            help='output JSON file', metavar='file.json')
    args = parser.parse_args()

    cfg = yaml.safe_load(args.src)
    args.src.close()
    output = generate_packer(cfg)
    json.dump(output, args.dest, indent=2, separators=(',', ': '))
    args.dest.write('\n') # json.dump doesn't write a final newline
    args.dest.close()
