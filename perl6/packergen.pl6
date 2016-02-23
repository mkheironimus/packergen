#! /usr/bin/env perl6

use v6;

use JSON::Pretty;
use YAMLish;

# If a config_template element exists, load that content (in order) and then
# overlay the supplied data. Otherwise just return the data.
multi expand_entry(%data where { %data<config_template>:exists } --> Hash) {
	my %new = %data<config_template>:delete.map({ load-yaml(slurp($^a)) });
	%(%new, %data);
}
multi expand_entry(%data --> Hash) {
	%data;
}

# Process templates and put the name in to a key of the resulting hash.
sub build(Pair (:key(:$name), :value(:$data)) --> Hash) {
	%(expand_entry($data), 'name' => $name);
}

# Process templates and add the global override definition if there isn't
# an override in the provisioner.
sub provision(%prov, %cfg --> Hash) {
	my %new = expand_entry(%prov);
	# I should describe the precedence of overrides in multiple places.
	if (%cfg<provisioner_override>:exists && !(%prov<override>:exists)) {
		%new<override> = %cfg<provisioner_override>;
	}
	%new;
}

# Process templates for a group of postprocessor entries or a single entry.
multi postproc(@post --> Seq) {
	@post.map({ expand_entry(%^a) });
}
multi postproc(%post --> Hash) {
	expand_entry(%post);
}

sub generate_packer(%cfg --> Hash) {
	# At least one builder definition is required by packer.
	my %pack = ( 'builders' => %cfg<builders>.map({ build($^a) }) );

	%pack<provisioners> = %cfg<provisioners>.map({ provision($^a, %cfg) })
			if (%cfg<provisioners>:exists);

	%pack<post-processors> = %cfg<post-processors>.map({ postproc($^a) })
			if (%cfg<post-processors>:exists);

	%pack<description> = %cfg<description> if (%cfg<description>:exists);

	%pack<variables>   = %cfg<variables>   if (%cfg<variables>:exists);

	%pack;
}

# --in=input.yaml --out=output.json
sub MAIN(Str :$in='', Str :$out='') {
	my %cfg = load-yaml(($in ne '') ?? slurp($in) !! $*IN.slurp-rest);

	my %output = generate_packer(%cfg);

	($out ne '') ?? spurt($out, to-json(%output)) !! say to-json(%output);
}

# vim: filetype=perl6
