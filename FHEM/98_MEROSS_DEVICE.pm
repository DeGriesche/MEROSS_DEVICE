package main;
use strict;
use warnings;

sub MEROSS_DEVICE_Initialize($) {
	my ($hash) = @_;

	$hash->{DefFn} = 'MEROSS_DEVICE_Define';
	$hash->{UndefFn} = 'MEROSS_DEVICE_Undef';
	$hash->{SetFn} = 'MEROSS_DEVICE_Set';
	$hash->{AttrFn} = 'MEROSS_DEVICE_Attr';
	$hash->{ShutdownFn} = "MEROSS_DEVICE_Shutdown";


	reloadPythonScript();
	AnalyzeCommand($hash, "set MEROSS_DEVICE getStatus");
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
		readingsBeginUpdate($hash);
		readingsBulkUpdate($hash, "position", "1");
		readingsEndUpdate($hash, 1);
	} elsif ($cmd eq "close") {
		readingsBeginUpdate($hash);
		readingsBulkUpdate($hash, "position", "0");
		readingsEndUpdate($hash, 1);
	} elsif ($cmd eq "position") {
		if ($args[0] eq 0) {
			readingsSingleUpdate($hash, "state", "close", 1);
		} else {
			readingsSingleUpdate($hash, "state", "open", 1);
		}
	} elsif ($cmd eq "getStatus") {
	} elsif ($cmd eq "getDeviceType") {
	} elsif ($cmd eq "reload") {
		reloadPythonScript();
	} elsif ($cmd eq "shutdown") {
	} else {
		return "Unknown argument $cmd, choose one of open:noArg close:noArg position:slider,0,100,100 getStatus:noArg getDeviceType:noArg reload:noArg shutdown:noArg" ;
	}
	return (undef, 0);
}

sub MEROSS_DEVICE_Attr(@) {
	my ($cmd,$name,$attr_name,$attr_value) = @_;
	if($cmd eq "set") {

	}
	return undef;
}

sub X_Shutdown ($) {
	my ( $hash ) = @_;
	AnalyzeCommand($hash, "set MEROSS_DEVICE shutdown");
}

sub reloadPythonScript() {
	my $runningProcesses = qx "pgrep -fl [m]eross_daemon.py | wc -l";
	if ($runningProcesses == "0") {
		{ system("python /opt/fhem/FHEM/meross/meross_daemon.py &") };
	}
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
