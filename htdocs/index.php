<?php
date_default_timezone_set('UTC');
$CONFIG = json_decode(file_get_contents(dirname(__FILE__)."/../config/settings.json"), TRUE);
?>
<html>

<head>
	<title>TallTowers - TEST</title>
	<style>
		h1,footer {
				   text-align: center;
		}
	</style>
</head>

<body bgcolor="grey">

	<h1>TallTowers Test Query</h1>
	<p>
		The purpose of this webpage is to test:
		<ul>
			<li>Webserver installation is working,</li>
			<li>Postgres can be queried with PHP script, using tt_web account, &amp;</li>
			<li>Results of query can be displayed to webpage.</li>
		</ul>
	</p>

	<h2>Security Note</h2>
	<p>
		This is publicliy visible.
	</p>
	
	<hr>
	
	<h4>start time of script execution</h4>
        <?php
                echo(date('Y-m-d H:i:s',time())),"-UTC";
        ?>

	<hr>
	
<!-- Query # 1 -->

	<h3>Query #1</h3>
	<p>Query the <b>Channels</b> table.</p>

	<?php
		$host=$CONFIG["dbconn"]["hostname"];
		$user="tt_web";
		$pass=$CONFIG["dbconn"]["dbpass"];
		$db="talltowers";
		$link=pg_Connect("host=$host dbname=$db user=$user password=$pass");
		$query1="SELECT * FROM Channels WHERE site='story' AND height=40";
		echo"<p>query1: <strong>",$query1,"</strong></p>";
		$result=pg_exec($link,$query1);
		$numrows=pg_numrows($result);
	?>
	<table border="1">
		<tr>
			<th>chn_id</th>
			<th>header</th>
			<th>height</th>
			<th>site</th>
			<th>unit</th>
		</tr>
		<?php
		   // Loop on rows in the result set. 
		   for($ri=0;$ri<$numrows;$ri++) {
				echo"<tr>\n";
				$row=pg_fetch_array($result,$ri);
				echo" <td>",$row["chn_id"],"</td>
				<td>",$row["header"],"</td>
				<td>",$row["height"],"</td>
				<td>",$row["site"],"</td>
				<td>",$row["unit"],"</td>
				</tr>
				";
			} pg_close($link);
		?>
	</table>

	<?php
		echo"<p>numrows = $numrows</p>";
		echo"<p><small>link = $link &nbsp &nbsp result = $result</small></p>";
	?>
	
	<hr>

<!-- Query # 2 -->

	<h3>Query #2</h3>
	<p>Query the <b>dat</b> table for story county's "WS_40m_NWht", and 
		calculate one min average, standard deviation, minimum, and maximum 
		gust, for the previous 2 hours from now.
		<br>
		<em>Note:</em> this is the maximum 3 second average wind speed within 
		the preceeding minute (and not recycling the window at the minute).
	</p>
	<?php
		$link=pg_Connect("host=$host dbname=$db user=$user password=$pass");
		$time=date('Y-m-d H:i:s',time() - 7200);
		$query2="WITH rolling AS (SELECT ts, val, avg(val) OVER(ORDER BY ts ROWS BETWEEN 3 preceding AND current row) AS mean3 FROM dat WHERE ts > '$time'::timestamp with time zone AND chn_id=1122 ORDER BY ts) SELECT date_trunc('minute', ts), avg(val), stddev(val), min(val), max(val), max(mean3) AS max3sec FROM rolling GROUP BY date_trunc('minute', ts) ORDER BY date_trunc('minute', ts) ASC Limit 240";
		echo"<p>query2: <strong>",$query2,"</strong></p>";
		$result=pg_exec($link,$query2);
		$numrows=pg_numrows($result);
	?>
	<table border="1">
		<tr>
			<th>TimeStamp (w/ TZ)</th>
			<th>Average</th>
			<th>Stand. Dev.</th>
			<th>Minimum</th>
			<th>Maximum</th>
			<th>Max Gust</th>
		</tr>
		<?php
		   // Loop on rows in the result set. 
		   for($ri=0;$ri<$numrows;$ri++) {
				echo"<tr>\n";
				$row=pg_fetch_array($result,$ri);
				echo" <td>",$row["date_trunc"],"</td>
				<td>",$row["avg"],"</td>
				<td>",$row["stddev"],"</td>
				<td>",$row["min"],"</td>
				<td>",$row["max"],"</td>
				<td>",$row["max3sec"],"</td>
				</tr>
				";
			} pg_close($link);
		?>
	</table>
	<?php
		echo"<p>numrows = $numrows</p>";
		echo"<p><small>link = $link &nbsp &nbsp result = $result</small></p>";
	?>
	
	<hr>
	
<!-- execution time -->

	<h4>end time of script execution</h4>
	<?php   
		echo(date("Y-m-d H:i:s",time())),"-UTC";
	?>
	<hr>

</body>

<footer text-align:center>
	<nav>author: Joe Smith</nav>
	date: 2016-Aug-7
</footer>

</html>
