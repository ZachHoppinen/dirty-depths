from pathlib import Path
import numpy as np
import pandas as pd
import shapely

from parsers import parse_boise, parse_cameron_pass, parse_fraser, parse_senator_beck

res = pd.DataFrame()

raw_dir = Path('SnowEx2021_TimeSeries_DepthTransects/raw')

parser = {'Boise River': parse_boise, 'Senator Beck': parse_senator_beck, \
          'Fraser': parse_fraser, 'Cameron Pass': parse_cameron_pass}

if __name__ == '__main__':

    for loc_dir in raw_dir.glob('*'):
        print(loc_dir)

        for date_dir in loc_dir.glob('*'):
            for fp in date_dir.joinpath('Depth Transects').glob('*'):
                df = parser[loc_dir.name](fp)
                df['date'] = pd.to_datetime(date_dir.name).strftime('%Y-%m-%d')
                df['Location'] = loc_dir.name
                res = pd.concat([res, df], ignore_index = True)
    # unreasonable values that could be in centimeters
    res.loc[:, 'depth'] = res.loc[:, 'depth'].astype(float)
    # res.loc[res.depth > 5, 'depth'] = res.loc[res.depth > 5, 'depth']/100
    # remove all other outliers ( > 10 meters) (n = 1) and Longitude > 1000 (n = 27)
    res = res.loc[res.depth < 1000]
    res = res.loc[res.geometry.y < 1000]
    # some observers in Boise River switched the lat and lon columns
    res.loc[res.geometry.y < 0, 'geometry'] = res[res.geometry.y < 0].geometry.map(lambda polygon: shapely.ops.transform(lambda x, y: (y, x), polygon))
    # some observers in Boise River put latitude in depth and doubled longitude (n = 2)
    res = res.loc[res.geometry.y > 0]
    # some observers in Boise River miss placed commas (n = 1)
    res = res[res.geometry.x < -30]

    res.to_csv('snowex_depths.csv')