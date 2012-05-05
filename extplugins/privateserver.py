#
# PrivateServer Plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2010 Mark Weirath (xlr8or@xlr8or.com)
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA    02110-1301    USA
#
# Changelog:
# v1.0.1 - 21/06/2010 - xlr8or - Debugged

__version__ = '1.0.1'
__author__  = 'xlr8or'

import b3
import b3.events
import b3.plugin
import b3.cron
import b3.functions
import os
import threading

#--------------------------------------------------------------------------------------------------
class PrivateserverPlugin(b3.plugin.Plugin):
    _allowedLevel = 2
    _guids = []
    _guidsfile = 'guids.txt'
    _ips = []
    _ipsfile = 'ips.txt'
    _kickMessage = '$player, You are not allowed to play, prepare to leave the arena.'
    _delay = 5
    _skillBased = False
    _minSkill = 0

    def startup(self):
        """\
        Initialize plugin settings
        """

        # get the admin plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # something is wrong, can't start without admin plugin
            self.error('Could not find admin plugin')
            return False
        
        # get the xlrstats plugin
        self._xlrstatsPlugin = self.console.getPlugin('xlrstats')
        if not self._xlrstatsPlugin:
            self.info('Could not find xlrstats plugin... Skillbased restriction is OFF.')
            self._skillBased = False
        else:
            self.verbose('Found XLRstats plugin, continueing...')
            try:
                self.playerstats_table = self._xlrstatsPlugin.playerstats_table
                self.verbose('Found XLRstats playerstats_table: %s' %self.playerstats_table)
            except:
                self.info('Xlrstats Playerstats table not found! Skillbased restriction is OFF.')
                self._skillBased = False
        if self._minSkill == 0:
            self._skillBased = False

        # register our commands
        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp

                func = self.getCmd(cmd)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)
        self._adminPlugin.registerCommand(self, 'psversion', 0, self.cmd_psversion, 'psver')

        # Register our events
        self.verbose('Registering events')
        self.registerEvent(b3.events.EVT_CLIENT_AUTH)
        
        # Loading Guids
        self.loadFromFile(self._guidsfile, 'guids')
        self.verbose('Loaded guids: %s' % self._guids)
        # Loading Ips
        self.loadFromFile(self._ipsfile, 'ips')
        self.verbose('Loaded guids: %s' % self._ips)

        self.debug('Started')

    def onLoadConfig(self):
        try:
            self._allowedLevel = self.config.getint('settings', 'allowedlevel')
        except:
            self.debug('using default setting')
            pass
        self.debug(self._allowedLevel)
        try:
            self._guidsfile = self.config.getpath('settings', 'guidsfile')
        except:
            self.debug('using default setting')
            pass
        self.debug(self._guidsfile)
        try:
            self._ipsfile = self.config.getpath('settings', 'ipsfile')
        except:
            self.debug('using default setting')
            pass
        self.debug(self._ipsfile)
        try:
            self._minSkill = self.config.getint('settings', 'minskill')
        except:
            self.debug('using default setting')
            pass
        self.debug(self._minSkill)
        try:
            self._kickMessage = self.config.get('settings', 'kickmessage')
        except:
            self.debug('using default setting')
            pass
        self.debug(self._kickMessage)
        try:
            self._delay = self.config.getint('settings', 'kickdelay')
        except:
            self.debug('using default setting')
            pass
        self.debug(self._delay)

        self._kickMessage = b3.functions.vars2printf(self._kickMessage)
        self.debug('PlayerRestricter loaded')
        return None

    def getCmd(self, cmd):
        cmd = 'cmd_%s' % cmd
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            return func

        return None

    def onEvent(self, event):
        """\
        Handle intercepted events
        """
        if not self.isEnabled:
            return None

        if event.type == b3.events.EVT_CLIENT_AUTH:
            self.checkPlayer(event.client)
        else:
            self.dumpEvent(event)

    def dumpEvent(self, event):
        self.debug('privateserver.dumpEvent -- Type %s, Client %s, Target %s, Data %s',
            event.type, event.client, event.target, event.data)

    def cmd_psversion(self, data, client, cmd=None):
        """\
        This command identifies Plugin version and creator.
        """
        cmd.sayLoudOrPM(client, 'I am PrivateServer Plugin version %s by %s' % (__version__, __author__))
        return None

    def checkPlayer(self, client):
        if self.isEnabled:
            _allowed = False
            # checking level
            if client.maxLevel >= self._allowedLevel and self._allowedLevel != 0:
                _allowed = True
                self.verbose('Level %s (%s) allowed' %(client.name, client.maxLevel) )
            # checking Guid
            if str(client.guid) in self._guids:
                _allowed = True 
                self.verbose('Found %s (%s) in Guid list' %(client.name, client.guid) )
            # checking IP
            if str(client.ip) in self._ips:
                _allowed = True
                self.verbose('Found %s (%s) in IP list' %(client.name, client.ip) )
            # checking Skill  
            if self._skillBased:
                playerStats = self._xlrstatsPlugin.get_PlayerStats(client)
                if playerStats.skill >= self._minSkill:
                    _allowed = True 
                    self.verbose('Skill %s (%s) sufficient to play' %(client.name, playerStats.skill) )

            if _allowed == False:
                self.debug('%s is not allowed to play, sending message.' % client.name)
                client.message(self._kickMessage % { 'player' : client.name } )
                t1 = threading.Timer(self._delay, self.delayedKick, (client,))
                t1.start()
            else:
                self.debug('%s is allowed to play, player is in the list.' % client.name)
        return None

    def delayedKick(self, client):
        self.debug('Kicking %s' % client.name)
        _reason = 'Player Restricted, %s was not allowed to play!' %client.name
        client.kick(_reason)

    def loadFromFile(self, fileName, _subj='guids'):
        if not os.path.isfile(fileName):
            self.error('%s file %s does not exist, disabling plugin!' %( _subj, fileName))
            self.disable()
            return False

        f = file(fileName, 'r')
        self.load(f.readlines(), _subj)
        f.close()

    def load(self, items=[], _subj='guids'):
        for w in items:
            w = w.strip()
            if len(w) > 1:
                if _subj == 'guids':
                    self._guids.append(w)
                elif _subj == 'ips':
                    self._ips.append(w)

if __name__ == '__main__':
  print '\nThis is version '+__version__+' by '+__author__+' for BigBrotherBot.\n'
