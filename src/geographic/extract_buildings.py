import subprocess
import tempfile
import zipfile
import os



def main():
    date = '251124'

    savedir = '/data/big/fmalveiro/complexity72/'
    zipped_osm = os.path.join(savedir, 'osm_data.zip')

    osmfile = f"somalia-{date}.osm.pbf"
    buildings_file = f"somalia-{date}-buildings.osm.pbf"

    
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zipped_osm, 'r') as zfile:
            zfile.extract(osmfile, tmpdir)
            
        mask = 'nwr/building'

        infile = os.path.join(tmpdir, osmfile)
        outfile = os.path.join(tmpdir, buildings_file)
        
        command = f"osmium tags-filter {infile} {mask} -o {outfile}"
        
        print('Extracting data...')
        subprocess.check_output(command, text=True, shell=True)
        
        with zipfile.ZipFile(zipped_osm, 'a') as zfile:
             print('Zipping...')
             zfile.write(outfile, arcname=buildings_file)
    
    return



if __name__ == '__main__':
    main()
