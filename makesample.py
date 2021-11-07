

# C:\\Windows\\Web 아래의 모든 jpg 파일을 검색한다.  
#  수십개의 jpg 파일이 있는 압축파일을 푼다.  
# 해당 폴더의 jpg를 축소하고 사이즈를 줄인다. 
# zip 파일을 다시 압축한다.  

# 위와 같은 zip 파일이 계속 요청이 들어온다.  
import sys 
from os import listdir
from os.path import isfile, join
from os import walk
import os
from typing import List
import tempfile
import zipfile
import shutil

ZIPARCHIVE = "ziptest"
ZIPWORK = "zipwork"

def get_jpgs(folder:str ) -> List[str]:
    result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(folder) for f in filenames if os.path.splitext(f)[1] == '.jpg']
    return result

def get_windows_wallpaper_jpgs() -> List[str]:

    if sys.platform == 'win32':
        local_jpg_repo = 'C:\\Windows\\Web'
    else:
        local_jpg_repo = '/mnt/c/Windows/Web' 
    return get_jpgs(local_jpg_repo)


def get_temporary_path(subfolder: str) -> str:
    """ 테스트를 위해 임시 폴더아래 서브폴더를 만들고 
    해당 위치에 zip 파일을 정한다.  
    """
    temp_path = os.path.join(tempfile.gettempdir(),subfolder)
    return temp_path

def copy_jpgs_to_temp_path():
    jpg_files = get_windows_wallpaper_jpgs()
    temp_path = get_temporary_path(ZIPARCHIVE)
    for i , file in enumerate(jpg_files):
        temp_file = "image" +str(i) + ".jpg" 
        newpath = os.path.join(temp_path,temp_file)
        if not os.path.exists(newpath):
            shutil.copy(file,newpath)



def make_test_zipfile():
     
    zip_path = get_temporary_path(ZIPARCHIVE)
    os.chdir(zip_path)
    copy_jpgs_to_temp_path()
    jpg_files = get_jpgs("./")
    test_zip_path = os.path.join(zip_path, "myzip.zip")
    with zipfile.ZipFile(test_zip_path, 'w') as myzip:
        for file in jpg_files:
            myzip.write(file)
    for file in jpg_files:
        os.remove(file)
    return test_zip_path


make_test_zipfile()








