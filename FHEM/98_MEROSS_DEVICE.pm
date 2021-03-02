package main;
use strict;
use warnings;

sub MEROSS_DEVICE_Initialize($) {
	my ($hash) = @_;

	$hash->{DefFn} = 'MEROSS_DEVICE_Define';
	$hash->{UndefFn} = 'MEROSS_DEVICE_Undef';
	$hash->{SetFn} = 'MEROSS_DEVICE_Set';
	$hash->{AttrFn} = 'MEROSS_DEVICE_Attr';
}

sub MEROSS_DEVICE_Define($$) {
	my ($hash, $def) = @_;
	my @param = split('[ \t]+', $def);
	my $name = $hash->{NAME};

	if(int(@param) != 3) {
		return "wrong number of parameters: define <name> MEROSS_DEVICE <deviceId>";
	}

	$hash->{name} = $param[0];
	$hash->{deviceId} = $param[2];
#	$attr{$name}{devStateIcon} = 'DEFAULT_OPERATION:nibe_mode_default@green AWAY_FROM_HOME:nibe_mode_away@yellow VACATION:nibe_mode_vacation@red';
#	$attr{$name}{icon} = "nibe_heatpump";

	AnalyzeCommand($hash, "set ".$name." getStatus");
	AnalyzeCommand($hash, "set ".$name." getDeviceType");

	return undef;
}

sub MEROSS_DEVICE_Undef($$) {
	my ( $hash, $name) = @_;
	DevIo_CloseDev($hash);
	RemoveInternalTimer($hash);
	return undef;
}

sub MEROSS_DEVICE_Delete ($$) {
	my ( $hash, $name ) = @_;
	# nothing to do
	return undef;
}

sub MEROSS_DEVICE_Set($@) {
	my ($hash, $name, $cmd, @args) = @_;

	return "\"set $name\" needs at least one argument" unless(defined($cmd));

	if ($cmd eq "open") {
		print("opening ".$name);
    } elsif ($cmd eq "close") {
		print("closing ".$name);
	} elsif ($cmd eq "getStatus") {
		#print("getStatus ".$name);
	} elsif ($cmd eq "getDeviceType") {
		#print("getDeviceType ".$name);
	} else {
    	return "Unknown argument $cmd, choose one of open close getStatus getDeviceType" ;
    }
}

sub MEROSS_DEVICE_Attr(@) {
	my ($cmd,$name,$attr_name,$attr_value) = @_;
	if($cmd eq "set") {

	}
	return undef;
}

1;

=pod
=item device

=begin html

<a name="MEROSS_DEVICE"></a>
<h3>MEROSS_DEVICE</h3>
<ul>
	<i>MEROSS_DEVICE</i> implements a binding to meross_iot</a>.
	<br><br>
	<a name="MEROSS_DEVICE_Define"></a>
	<b>Define</b>
	<ul>
		<code>define &lt;name&gt;  MEROSS_DEVICE &lt;deviceId&gt; </code><br><br>
		&lt;deviceId&gt; specifies the <i>Identifier</i> from your MEROSS UI
		<br><br>
		Example: <br>
		<code>define MySwitch MEROSS_DEVICE 8s23vf8sw2s</code>
	</ul>
	<br>

</ul>

=end html

=cut
