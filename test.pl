#!/usr/bin/perl -w

use Data::Dumper;
use Paws;
use Paws::Glacier;

my $paws = Paws->new(config => { credentials => {
        access_key	=> 'AKIAJQQGEYEGRQMNI6FA',
        secret_key	=>	'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'
}, region => 'eu-west-2' });
my $glacier = $paws->service('Glacier');

my $res = $glacier->ListVaults(
    AccountId	=> 
    Limit	=> 10,
    Marker	=> 1
);

print "$res\n";
exit;

=comment
use Net::Amazon::Glacier;
 
$glacier = Net::Amazon::Glacier->new(
        'us-west-2',
        'AKIAJQQGEYEGRQMNI6FA',
        'lJ9TVF7sBfMzQa7Osqoe8da35y/bE3Ef9pWZF6gk',
);
 
my $vault = 'Test';

$archive_id = 'aavkBdVfS-JswxokGi5TX7DvzCD5fCues-b27FyZfcF5Dei9KN-KwL3tvuh0wvo2_bX8nz5q6JA_eySVzb4O58Z03v8Dxd_N_LwVAAFeYzlmtVtRcex7phLiUCFsD1MmwNyovEpS0g';
print $glacier->simple->download( $archive_id || 'description', [ $ranges ] );
exit;

#print "=list_jobs=\n";
#print Dumper($glacier->list_jobs($vault));
#print "======\n";



#print "=list_vaults=\n";
my @vaults = $glacier->list_vaults();
print Dumper (\@vaults);
print "======\n\n";

foreach $val  (@{$vaults[0]}) {
	my $name = $val->{'VaultName'};
	print "$name\n======\n";

	my $events = ["ArchiveRetrievalCompleted", "InventoryRetrievalCompleted"];
	print $glacier->get_vault_notifications($name, $val->{'VaultARN'}, $events);
#	print $_->{'VaultName'};
	print "======\n";
}
print "\n";

=cut
