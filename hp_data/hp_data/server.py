import logging
import json
import numpy as np
from flask import Flask
from flask_apispec import use_kwargs

from hp_data import controller as cnt
from hp_data import utils as ut
from hp_data import schemas


log = logging.getLogger(__name__)
appFlask = Flask(__name__)


def _append_to_data(df, col_names, data, data_lens):
    """Will build up the data dict to send to the front end.

    Args:
        df: Input data (from controller)
        col_names: The names of extra columns all with the same value
        data: dict that will store the data to pass to the frontend
    """
    max_len = data_lens['max']
    data_lens['len'] += len(df)
    if data_lens['len'] > max_len:
        remainder = data_lens['len'] - max_len
        if remainder > len(df):
            return data
        else:
            df = df.iloc[:remainder]


    for col in df.columns:
        if df.dtypes[col] == 'category':
            data.setdefault(col, []).extend([list(map(int, i)) for i in ut.huffman(df[col].cat.codes.values) if i])

        elif df.dtypes[col] == 'datetime64[ns]':
            ret = [[np.datetime_as_string(i[0], 'D'), i[1]]
                   for i in ut.huffman(df[col].values)]
            data.setdefault(col, []).extend(ret)

        else:
            if col in {'price', 'postcode', 'paon', 'street'}:
                if col == 'price':
                    data.setdefault(col, []).extend(list(map(int, df[col].values)))
                else:
                    data.setdefault(col, []).extend(list(df[col].values))
            else:
                data.setdefault(col, []).extend(ut.huffman(df[col].values))

    for col, val in col_names:
        data.setdefault(col, []).append([val, len(df)])

    return data


@appFlask.route('/', methods=['POST'])
@use_kwargs(schemas.SelectorsSchema)
def index(**selectors):
    """Will query the datacache and return a json object with any relevant data"""
    if 'max_data_len' in selectors:
        max_data_len = selectors.get('max_data_len')
        selectors.pop('max_data_len')
    else:
        max_data_len = int(4e5)

    # Create data generator
    try:
        cont = cnt.DataController(selectors, ['date_transfer', 'price', 'paon', 'street',
                                              'city', 'county', 'postcode',])
        data = cont.read_data()
    except Exception as e:
        log.error('Exception: ', e)
        return 1

    # Now actually read the data (first 10,000 lines)
    data_len = 0
    ret_data = {}
    data_lens = {'len': 0, 'max': max_data_len}

    try:
        for df, col_names in data:
            ret_data = _append_to_data(df,
                                       col_names,
                                       ret_data,
                                       data_lens)


            if data_lens['len'] > max_data_len:
            #    ret_obj['err_msg'] = (f'Only the first {_max_data_len:,} results are being passed back from the server. '
            #                          f'Please narrow your search to see all data.')
                break
    except Exception as e:
        log.error('Data Read Failure', exc_info=e)
        return 1

    return json.dumps(ret_data)


appFlask.run(port=8008)
