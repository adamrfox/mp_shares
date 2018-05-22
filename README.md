# mp_shares
A script to view multi-protocol shares (IN DEVELOPMENT) .  Requires the 'requests' module

The idea here is to use the API to figure out what shares are multi-protocol (i.e. both NFS exports and SMB shares point to them).
There is no native way to do this in OneFS.  Here's the basic idea behind the script:

I'm only looking for matches within an access zone.  It's possible in 8.x to have overlapping zones (and System always overalps everyone)
but for the first release I'm settling for within zone.  Access zones are auto-discovered by default, although the user can supply a list
of access zones if desired in order to exclude some.  

By default it looks for a full match, although the user can do a partial match with
the -p flag.  Partial matches meet the following rules:

  1. If the path is the exact root of the access zone (incluind /ifs for the System zone), it reverts to an exact match because this would
  match everything by definition (e.g. a share with /ifs matches every share in the System zone since all paths start with /ifs, not
  particularly interesting).
  
  2. Assuming the path is not at the root of an access zone, the match is left to right, not a substring in the middle as I don't think 
  that makes sense in this context, although I'm open to counter-arguements on this.  So /ifs/data would match /ifs/data/project1 since 
  one encompassees the other.  Again, this only happens if the -p flag is applied.  By default only exact matches are flagged.
  
Since the script uses the API, it can be run anywhere that has Python, including the cluster itself.  If running on the cluster, there is
no need to specify a cluster name as "localhost" is assumed. If runnign off-cluster, a cluster name or IP in the System zone must be
supplied.

Additionally, since the API is used, credentials must be supplied.  This can be the root credentials, but it's not requred.  The 'admin' 
user would suffice as would any user that has the RBAC privledges ISI_PRIV_LOGIN_PAPI, ISI_PRIV_SMB (r/o), ISI_PRIV_NFS (r/o), and 
ISI_PRIV_AUTH (r/o).

Example Syntax:

client% mp_shares.py cluster1

This would scan all access zones on cluster1 for multi-protocol shares

client% mp_shaers.py -z zone1 cluster1

This would look for multi-protool shares only in access zone 'zone1'

client% mp_shares.py -z System,zone1 cluster1

This would look for multi-protocol shares in zones 'System' and 'zone1'

client% mp_shares.py -p cluster1

This would look for partial path matches in all access zones.
  
