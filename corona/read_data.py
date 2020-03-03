from csv import DictReader
from glob import glob
from datetime import datetime
from corona.file_names import file_names


def read_data_raw():
    filename = file_names['ts_data']
    return list(DictReader(open(filename, 'r', encoding='utf-8-sig')))


def get_jh_files():
    return sorted(glob(file_names['jh_dir_update']+'/*2020.csv'))


def str2float(string):
    if string == '':
        return 0
    return int(string)


def process_jh_record(record):
    for tag in ['Confirmed', 'Recovered', 'Deaths']:
        record[tag.lower()] = str2float(record[tag])
        del record[tag]

    record['last_update'] = record['Last Update']
    del record['Last Update']

    record['report_date'] = datetime.strptime(record['report_date_string'], '%m-%d-%Y')
    record['country'] = record['Country/Region']
    record['province'] = record['Province/State']
    del record['Country/Region'], record['Province/State']


def read_jh_data():
    files = get_jh_files()
    data = []
    for file in files:
        report_data = list(DictReader(open(file, 'r', encoding='utf-8-sig')))
        for line in report_data:
            report_date = file.split('/')[-1].split('.csv')[0]
            line['report_date_string'] = report_date
            process_jh_record(line)
        report_data = [dict(line) for line in report_data]
        data.extend(report_data)
    return data


def get_countries(jh_data=None, province=False):
    if jh_data is None:
        jh_data = read_jh_data()

    sep = ' // '
    if province:
        def func(x):
            return x['country'] + sep + x['province']
    else:
        def func(x):
            return x['country']

    return sorted({func(r) for r in jh_data})
