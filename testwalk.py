import os
from os import walk
import sys

if sys.platform == 'win32':
    local_jpg_repo = 'C:\\Windows\\Web'
else:
    local_jpg_repo = '/mnt/c/Windows/Web' 

# for dp, dn, filenames in os.walk(local_jpg_repo):
#     for f in filenames:
#         if os.path.splitext(f)[1].lower() == '.jpg':
#             print(os.path.join(dp,f))

# jpgfiles = [ os.path.join(dp,f) 
#                 for dp, _ ,filenames in os.walk (local_jpg_repo)
#                     for f in filenames
#                         if os.path.splitext(f)[1].lower() == '.jpg']
jpgfiles = [ os.path.join(dp,f) for dp, _ ,filenames in os.walk (local_jpg_repo)
                for f in filenames
                    if os.path.splitext(f)[1].lower() == '.jpg']
#print(os.environ['TMPDIR'])
print(os.environ)



