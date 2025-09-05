"""
Download osm data from geofabrik.
"""

import urllib.request as urlrequest
import urllib.error as urlerror

import zipfile

import datetime
import os



def main():
    download_date = 'latest'

    if download_date != 'latest':
        raise NotImplementedError('We can download a specific date from geofabrik available files. Go program it if you need it :)')
    else:
        date = datetime.datetime.today().date().strftime('%y%m%d')


    savedir = './data/'
    savezip = 'osm_data.zip'
    savefile = f"somalia-{date}.osm.pbf"

    download_path = os.path.join(savedir, savefile)
    download_file = f"somalia-{download_date}.osm.pbf"
    

    
    url = f"https://download.geofabrik.de/africa/{download_file}"
    
    
    # download osm data from geofabrik
    try:
        print(f"Downloading {savefile} from {url}...")
        savepath, msg = urlrequest.urlretrieve(url, download_path)
    except urlerror.HTTPError:
        raise ValueError(f'{url} is not available.')
    except Exception as e:
        raise e


    # save into zipfile to keep things tidy
    savepath = os.path.join(savedir, savezip)

    print(f"Saving into zipfile: {savepath}...")
    with zipfile.ZipFile(savepath, 'w') as zfile:
        zfile.write(download_path)

    
    return



if __name__ == '__main__':
    main()
