import subprocess
import sys
import argparse

#from plexapi.myplex import MyPlexAccount

import plexapi

from plexapi.myplex import MyPlexAccount
account = MyPlexAccount('c_mobile@hotmail.com', 'imagine00')
plex = account.resource('firewall').connect()  # returns a PlexServer instance

#from plexapi.server import PlexServer
#baseurl = 'http://10.0.0.2:32400'
#token = ''
#plex = PlexServer(baseurl, token)

#print(plex)
shows = plex.library.section('TV Shows')
for video in shows.search():
    for episode in video.episodes():
        print(f"{video.title}-{episode.seasonEpisode}:{episode.isPlayed}")

print(plex)
