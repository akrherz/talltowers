<?php
$CONFIG = json_decode(file_get_contents(dirname(__FILE__)."/../config/settings.json"), TRUE);
?>
<html>

<head>
	<title>Iowa Atmospheric Observatory TallTowers Data Website</title>
	<style>
		h1,footer {
				   text-align: center;
		}
	</style>
</head>
<body>

<h1>Iowa Atmospheric Observatory TallTowers Data Website</h1>

<p><strong>Tall tower data:</strong> 1-Hz data collection from June 2016 to
September 2021.  20-Hz data collection recorded episodically starting
November 2016. <a href="#towers">Link</a></p>

<p><strong>Sodar data</strong> recorded from May 2018 to June 2021.  
<a href="#sodar">Link</a></p>

<p><strong>Surface met station data</strong> recorded from November 2018
until October 2021. <a href="#surface">Link</a></p>

<p>For more information about these data please contact: 
Daryl Herzmann (akrherz@iastate.edu)</p>

<h3>***Data Disclaimer***</h3>

<p>Please acknowledge the following sources of support for the IAO and the
    FaNTASTIC project for any use of these data in publications, presentations,
    or any other academic or industry research application: 
    NSF/EPSCoR grant to the state of Iowa (Grant #1101284),
    a follow-on NSF/AGS grant #1701278, and Opportunity Grant (#OG-17-001)
    from the Iowa Economic Development Authority (formerly Iowa Energy Center). 
</p>


<p><a name="tower">Tall tower Data</a></p>

<ul>
    <li>Raw netCDF data files: <a href="/netcdf/">Link</a></li>
    <li>IEM plotting tool to display and download limited time periods of data:
        <a href="https://mesonet.agron.iastate.edu/plotting/auto/?q=158">Link</a></li>
    <li>IEM 1-min analog data download tool for 1-minute to 1-hour statistics:
        <a href="https://mesonet.agron.iastate.edu/projects/iao/analog_download.php">Link</a></li>
    <li>Tall tower metadata (tower servicing, instrumentation, and field condition logs):
        Link #6.</li>
</ul>

<p><a name="sodar">Sodar Data</a></p>

<ul>
    <li>IEM 10-minute data download tool: here [Link #4]</li>
    <li>Description of instrument operation and metadata: here [Link #7]</li>
</ul>


<p><a name="surface">Surface met station Data</a></p>

<ul>
<li>IEM 10-minute data download tool: here [Link #5]</li>
<li>Surface met station metadata: here [Link #8]</li>
</ul>

</body>
</html>
