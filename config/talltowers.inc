
  DocumentRoot /opt/talltowers/htdocs
  
  <Directory "/opt/talltowers/htdocs">
    Options Indexes MultiViews FollowSymLinks
    AllowOverride All
  </Directory>
  
  Alias "/plots" "/opt/talltowers/webplots"
  <Directory "/opt/talltowers/webplots">
    Options Indexes MultiViews FollowSymLinks
    AllowOverride All
  </Directory>

    # Raw netcdf files
    Alias "/netcdf" "/mnt/talltowers"
    <Directory "/mnt/talltowers">
      Options Indexes MultiViews FollowSymLinks
      AllowOverride All
    </Directory>
