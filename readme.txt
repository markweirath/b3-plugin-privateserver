###################################################################################
#
# Plugin for B3 (www.bigbrotherbot.net)
# (c) 2010 Mark Weirath (xlr8or@xlr8or.com)
#
# This program is free software and licensed under the terms of
# the GNU General Public License (GPL), version 2.
#
# http://www.gnu.org/copyleft/gpl.html
###################################################################################

PrivateServer (v1)
###################################################################################

This plugin makes a private server based on level, guid or ip address.

First the plugin checks if a player has a certain level at which he is allowed to 
connect, if the level is not reached it checks against two files with guids/ips 
(one guid/ip per line) and checks if connecting players is on one of those lists.
If not, a message is displayed and the player kicked.

Requirements:
###################################################################################

- B3 version 1.1.0 or higher


Installation:
###################################################################################

1. Unzip the contents of this package into your B3 folder. It will
place the .py file in b3/extplugins and the config file .xml in
your b3/extplugins/conf folder.

2. Open the .xml file with your favorit editor and modify the
settings if you want them different.

3. Open your B3.xml file (in b3/conf) and add the next line in the
<plugins> section of the file:

<plugin name="privateserver" config="@b3/extplugins/conf/privateserver.xml"/>

4. Place the guids.txt and ips.txt files in the b3/extplugins/conf folder, or 
modify the path to the file in playerrestricter.xml. Add the guids and/or ips
to the appropriate files, one per line.

Changelog
###################################################################################
v1.0.0         : Initial release
v1.0.1         : Bugfix


###################################################################################
xlr8or - 2 august 2010 - www.bigbrotherbot.net // www.xlr8or.com
