Iowa State University
Iowa Atmospheric Observatory
Tall Towers Monthly Analog File README

Website: https://mesonet.agron.iastate.edu/projects/iao/

Summary
=======

This directory contains netCDF formatted files with monthly data from the "tall towers",
which are a part of the Iowa Atmospheric Observatory.  At five minute intervals,
the 1 hertz data is statistically summarized.  The following statistical summaries
are identified as such:

 - 'mean', the arithmetic mean.
 - 'median', the median value.
 - 'minimum', the smallest value.
 - 'maximum', the largest value.
 - 'standard_deviation', the standard deviation of the dataset.
 - 'median_abs_deviation', the median of the absolute value difference between an 
 individual observation and the median value.
 - 'count', the number of observations included within the five minute window.

Time Statistics
===============

A window of five minutes is considered for the statistics.  This window is defined by
the minute past the hour modulo five (inclusive) until the next minute past the hour
modulo five (exclusive).  For example, 00:00:00 until 00:04:59.

NetCDF Variable Naming Nomenclature
===================================

The naming nomenclature of the variables found in the NetCDF file are the combination
of the observation datum combined with the statistical label and separated by a single
underscore.  The observation datums are the combination of variable type, observation
height above ground and the orientation of that sensor from the tower.  For example,
'ws_5m_s' is the south mounted wind speed reading at 5 meters AGL.

The variable types are as follows:

- airtc, air temperature.
- bp, pressure.
- rh, relative humidity.
- winddir, wind direction.
- ws, wind speed.

Questions/Comments?
===================

Please email the group at isuiao@iastate.edu.
