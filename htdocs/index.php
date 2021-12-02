<?php
$CONFIG = json_decode(file_get_contents(dirname(__FILE__)."/../config/settings.json"), TRUE);
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

<h1>Iowa Atmospheric Observatory TallTowers Data Website</h1>

<ul>
    <li><a href="/netcdf/">Raw NetCDF Data Files</a></li>
</ul>

</body>
</html>
