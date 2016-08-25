<?php
date_default_timezone_set('UTC');
$CONFIG = json_decode(file_get_contents(dirname(__FILE__)."/../config/settings.json"), TRUE);

function get_vnames($vname, $level){
	if ($vname == 'ws'){
		$v1 = sprintf("ws_%sm_s", $level);
		$extra = "";
		if ($level == 10 || $level == 40 || $level == 120) $extra = "ht";
		$v2 = sprintf("ws_%sm_nw%s", $level, $extra);
		return Array($v1, $v2);
	} else if ($vname == 'winddir'){
		$v1 = sprintf("winddir_%sm_s", $level);
		$v2 = sprintf("winddir_%sm_nw", $level);
		return Array($v1, $v2);
	} else if ($level == 120 && ($vname == 'airtc' || $vname == 'rh')){
		$v1 = sprintf("%s_%sm_1", $vname, $level);
		$v2 = sprintf("%s_%sm_2", $vname, $level);
		return Array($v1, $v2);
	}
	$v1 = sprintf("%s_%sm", $vname, $level);
	return Array($v1);
}
function pp($val){
	if ($val == null) return "M";
	return sprintf("%.2f", $val);
}
function get_last($conn, $table, $tower){
	$rs = pg_query($conn, "SELECT * from data_$table WHERE tower = $tower and ".
		"valid > (now() - '6 hours'::interval) ORDER by valid DESC LIMIT 1");
	if (pg_numrows($rs) == 1){
		return pg_fetch_assoc($rs, 0);
	}
	return null;
}

$host=$CONFIG["webdbconn"]["hostname"];
$user="tt_web";
$pass=$CONFIG["webdbconn"]["dbpass"];
$db="talltowers";
$conn = pg_Connect("host=$host dbname=$db user=$user password=$pass");
pg_query($conn, "SET TIME ZONE 'UTC'");

$data = Array();
$tables = Array("monitor", "sonic", "analog");
$towers = Array("hamilton", "story");
while( list($towerid, $towername) = each($towers)){
	reset($tables);
	while( list($key, $table) = each($tables)){
		$data[$towerid][$table] = get_last($conn, $table, $towerid);
	}
}

$latest = "<table cellpadding=\"3\" border=\"1\" cellspacing=\"0\"><tr>";
reset($towers);
while (list($towerid, $tower) = each($towers)){
	$latest .= "<td><h3>$tower</h3>";
	reset($tables);
	while (list($key, $table) = each($tables)){
		$latest .= sprintf("<p><strong>%s</strong>: %s",
				$table, @$data[$towerid][$table]["valid"]);
	}
	$latest .= "</td>";
}
$latest .= "</tr></table>";

$table = <<<EOF
<table><tr>
EOF;
$levels = Array(120, 80, 40, 20, 10, 5);
$columns = Array("sonic" => Array("ux", "uy", "uz", "ts", "diag"),
		"monitor" => Array("boardtemp", "boardhumidity", "inclinepitch",
				"inclineroll"),
		"analog" => Array("ws", "winddir", "rh", "airtc"));
while (list($key, $level) = each($levels)){
	$table .= sprintf("<td valign=\"top\">
	<table border=\"1\" cellpadding=\"3\" cellspacing=\"0\">
	<thead>
		<tr><th colspan=\"3\">%s m</th></tr>
		<tr><th>Variable</th><th>Hamiliton</th><th>Story</th></tr>
	</thead>
	<tbody>", $level);				
	reset($columns);
	while (list($tablename, $vnames) = each($columns)){
		reset($vnames);
		while (list($key, $vname) = each($vnames)){
			if ($key == 0 && $tablename == 'sonic'){
			} else {
				$table .= "<tr>";
			}
			$vnames2 = get_vnames($vname, $level);
			//echo sprintf("<br />%s :: %s :: %s :: %s", $vname, $level,
			//		$tablename, $vnames2[0]);
			while (list($key3, $col) = each($vnames2)){
				$ham = @$data[0][$tablename][$col];
				$sto = @$data[1][$tablename][$col];
				$table .= sprintf("<td>%s</td><td>%s</td><td>%s</td></tr>", 
						$col,
						pp($ham), pp($sto));
			}				
		}
	}
	$table .= "</tbody></table></td>";
}
$table .= "</td></tr></table>";
?>
<html>

<head>
	<title>TallTowers Latest Data</title>
	<style>
		h1,footer {
				   text-align: center;
		}
	</style>
</head>
<body>
	<h1>TallTowers Latest Data</h1>

<a href="/plots/">Recent Diagnostic Plots</a>
<br />

<?php echo $latest; ?>
<?php echo $table; ?>


</body>
</html>
