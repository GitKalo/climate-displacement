"""
Get a osm file with only the roads.
"""

# filter out components of the osm.pbf file that make out roads

import subprocess
import tempfile
import zipfile
import os


def main():
    date = '250905'
    
    savedir = './data/'
    zipped = f"{savedir}/osm_data.zip"
    osmfile = f"somalia-{date}.osm.pbf"
    savefile = f"somalia-{date}-highways.osm.pbf"


    
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zipped, 'r') as zfile:
            zfile.extract(osmfile, tmpdir)

        loadpath = os.path.join(tmpdir, osmfile)
        savepath = os.path.join(tmpdir, savefile)
        
        command = f"osmium tags-filter {loadpath} w/highway -o {savepath}"


        try:
            subprocess.run(command, shell=True, check=True, capture_output=True)
        except subprocess.CalledProcessError as error:
            print(error.stderr)
            raise error

        print(os.listdir(tmpdir))

        with zipfile.ZipFile(zipped, 'a') as zfile:
            zfile.write(savepath, arcname=savefile)
    
    return



if __name__ == '__main__':
    main()
