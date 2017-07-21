Nik Collection for GIMP
===

Installation script to install Nik Collection for use with GIMP (2.9 & 2.10) and as a standalone app. 

Screenshots:

![](images/screen_1.png)


![](images/screen_2.png)


![](images/screen_3.png)

### Notes:

* Tested on Ubuntu 17.04 with Wine Staging v2.12 using Nik Collection v1.2.11, and GIMP v2.9.5 (from git).
* Depending on your system specs the plugins can take some time to start as they are launched through wine.
* Updated install script now verifies for GIMP version and related packages required to make it all work.

### Issues:

* GIMP will complain with the message 'Incompatible type for "RichTIFFIPTC"; tag ignored' after using some of the apps. If you click ok, the error will go away and everything will work. Note that if you have the convert utility program installed from the imagemagick package those warnings will disappear, though the installer now asks if you want to install the correct package if it is missing.

### Credits:

* Initial scripts and information was had from Erico Porto at https://github.com/ericoporto/NikInGimp (his version required PlayOnLinux, if you prefer it rather than using standard wine or wine staging these plugins do then definitely give it a try).

