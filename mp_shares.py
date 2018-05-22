#!/usr/bin/python

import sys
sys.path.append (".")
import requests
import getopt
import re
import json
import getpass
import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Shares():

  def __init__(self, zone, root):
    self.zone = zone
    self.zone_root = root
    self.nfs = []
    self.smb_name = []
    self.smb_path = []
  
  def get_zone_root (self):
    return (self.zone_root)
    
  def add_nfs_path (self, path):
    self.nfs.append(path)
    
  def get_nfs_path (self, i):
    return (self.nfs[i])
  
  def add_smb_share (self, name, path):
    self.smb_name.append(name)
    self.smb_path.append(path)
    
  def get_smb_share(self, i):
    return ([str(self.smb_name[i]), str(self.smb_path[i])])
    
def api_call (url, user, password):
  resp = requests.get (url, verify=False, auth=(user,password)).json()
  try: resp['errors']
  except KeyError: return (resp)
  sys.stderr.write ("ERROR: " + resp['errors'][0]['message'])
  exit (1)

cluster = "localhost"
zone_data = []
zones = []
all_zones = True
full_match = True

optlist, args = getopt.getopt (sys.argv[1:], 'hz:p', ["help", "zone=", "partial"])
for opt, a in optlist:
  if opt in ('-z', '--zone'):
    af = a.split(',')
    for x in af:
      zones.append (x)
    all_zones = False
    
  if opt in ('-p', "--partial"):
    full_match = False
    
if len(args) == 1:
  cluster = args[0]
url_head = "https://"+cluster+":8080/platform/3/"
user = raw_input ("User: ")
password = getpass.getpass ("Password: ")
url = url_head + "zones"
data = api_call (url, user, password)
for i, x in enumerate(data['zones']):
  if all_zones == True or data['zones'][i]['id'] in zones:
    zone_data.append(Shares(data['zones'][i]['id'], data['zones'][i]['path']))
for z, w in enumerate(zone_data):
  resume = True
  first = True
  while resume == True:
    if first == True:
      url = url_head + "protocols/nfs/exports?zone="+zone_data[z].zone
    else:
      url = url_head + "protocols/nfs/exports?zone="+zone_data[z].zone+"&resume="+resume_key
    data = api_call (url, user, password)
    if data['resume'] is None:
      resume = False
    else:
      resume_key = data['resume']
      first = False
    for i, x in enumerate(data['exports']):
      for j, y, in enumerate(data['exports'][i]['paths']):
        zone_data[z].add_nfs_path(data['exports'][i]['paths'][j])
  resume = True
  first = True
  while resume == True:
    if first == True:
      url = url_head + "protocols/smb/shares?zone="+zone_data[z].zone
    else:
      url = url_head + "protosols/smb/shares?zone="+zone_data[z].zone+"&resume="+resume_key
    data = api_call (url, user, password)
    if data['resume'] is None:
      resume = False
    else:
      resume_key = data['resume']
      first = False
    for i, x in enumerate (data['shares']):
      zone_data[z].add_smb_share(data['shares'][i]['name'], data['shares'][i]['path'])
print "Zone:,NFS Path,SMB Path,SMB Share Name:"
for z, x in enumerate (zone_data):
  for p, y in enumerate (x.nfs):
    nfs_path = x.get_nfs_path(p)
    for s, q in enumerate (x.smb_name):
      [smb_name, smb_path] = x.get_smb_share(s)
      if full_match == True:
        if nfs_path == smb_path:
          print x.zone + "," + nfs_path + "," + smb_path + "," + smb_name
      else:
        if nfs_path == x.get_zone_root():  
          if nfs_path == smb_path:
            print x.zone + "," + nfs_path + "," + smb_path + "," + smb_name
        else:
          nfs_len = len(nfs_path)
          smb_len = len(smb_path)
          if nfs_len > smb_len:
            if nfs_path.startswith(smb_path):
              print x.zone + "," + nfs_path + "," + smb_path + "," + smb_name
          elif smb_len > nfs_len:
            if smb_path.startswith(nfs_path):
              print x.zone + "," + nfs_path + "," + smb_path + "," + smb_name
          else:
            if nfs_path == smb_path:
              print x.zone + "," + nfs_path + "," + smb_path + "," + smb_name
        