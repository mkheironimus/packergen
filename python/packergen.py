#! /usr/bin/env python2

import argparse
import json
import sys
import yaml

class PackerGen(object):
    """Load and process YAML source in to Packer JSON."""

    def __init__(self, handle=None):
        """Read and process YAML from a filehandle, if specified."""
        self.cfg = {}
        self.output = {}
        if handle is not None:
            self.load(handle)


    def load(self, handle=sys.stdin):
        """Load and process YAML source from filehandle."""
        self.cfg = yaml.safe_load(handle)
        self.generate()


    def save(self, handle=sys.stdout):
        """Save JSON output to filehandle."""
        json.dump(self.output, handle, indent=2, separators=(',', ': '))
        handle.write('\n') # json.dump doesn't write a final newline


    def load_yaml(self, name):
        """Utility function to import a YAML file."""
        y = open(name, 'r')
        yml = yaml.safe_load(y)
        y.close()
        return yml


    def expand_entry(self, entry):
        """Load all of the templates in an entry."""
        new = {}
        if 'config_template' in entry:
            if type(entry['config_template']).__name__ == 'str':
                new.update(self.load_yaml(entry['config_template']))
            else:
                [new.update(self.load_yaml(tmpl))
                        for tmpl in entry['config_template']]
            del entry['config_template']
        new.update(entry)
        return new


    def build(self, name, builder):
        """Process and return a single builder."""
        b = self.expand_entry(builder)
        b['name'] = name
        return b


    def provision(self, prov, cfg):
        """Process and return a single provisioner."""
        p = self.expand_entry(prov)
        if 'provisioner_override' in cfg and not 'override' in prov:
            p['override'] = cfg['provisioner_override']
        return p


    def postproc(self, post):
        """Process and return a postprocessor entry, which can be either a
        single postprocessor or a group (array) of postprocessors."""
        return self.expand_entry(post) if type(post).__name__ == 'dict' else [
                self.expand_entry(p) for p in post ]


    def generate(self):
        self.output = { 'builders': [] }
        for name, builder in self.cfg['builders'].iteritems():
            self.output['builders'].append(self.build(name, builder))

        if 'provisioners' in self.cfg:
            self.output['provisioners'] = [self.provision(p, self.cfg)
                    for p in self.cfg['provisioners']]

        if 'post-processors' in self.cfg:
            self.output['post-processors'] = [self.postproc(p)
                    for p in self.cfg['post-processors']]

        if 'description' in self.cfg:
            self.output['description'] = self.cfg['description']

        if 'variables' in self.cfg:
            self.output['variables'] = self.cfg['variables']

        return self.output


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

    pg = PackerGen(handle=args.src)
    args.src.close()
    pg.save(args.dest)
    args.dest.close()
