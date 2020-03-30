from csv import DictReader
from glob import glob
from datetime import datetime
from datetime import timedelta
import os
from corona.file_names import file_names, data_dir


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

    record['report_date'] = datetime.strptime(record['report_date_string'], '%Y-%m-%d')
    record['country'] = record['Country/Region']
    record['province'] = record['Province/State']
    del record['Country/Region'], record['Province/State']


def process_jh_record_new(record):
    for tag in ['Confirmed', 'Recovered', 'Deaths']:
        record[tag.lower()] = str2float(record[tag])
        del record[tag]

    record['last_update'] = record['Last_Update']
    del record['Last_Update']

    record['report_date'] = datetime.strptime(record['report_date_string'], '%Y-%m-%d')
    record['country'] = record['Country_Region']
    record['province'] = record['Province_State']
    del record['Country_Region'], record['Province_State']


def read_jh_data():
    files = get_jh_files()
    data = []
    for file in files:
        print('file: %s' % file)
        report_data = list(DictReader(open(file, 'r', encoding='utf-8-sig')))
        for line in report_data:
            report_date = file.split('/')[-1].split('.csv')[0]
            # fix date to YYYY-MM-DD
            month, day, year = report_date.split('-')
            report_date = '%s-%s-%s' % (year, month, day)
            line['report_date_string'] = report_date
            if report_date < '2020-03-22':
                # old format
                process_jh_record(line)
            else:
                # read new format
                process_jh_record_new(line)

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


def european_countries(include_italy=True):
    countries = {'France', 'Spain', 'UK', 'Sweden', 'Switzerland',
                 'Portugal', 'Germany', 'Romania', 'North Ireland',
                 'Netherlands', 'Norway', 'Luxembourg', 'Ireland',
                 'Iceland', 'Greece', 'Finland', 'Denmark', 'Croatia',
                 'Belgium', 'Austria', 'Andora'}

    if include_italy:
        countries.add('Italy')

    return countries


def is_europe(country, include_italy=True):
    countries = european_countries(include_italy=include_italy)
    return country in countries


def get_ecdc_file(year, month, day):
    date_string = str(year) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2)
    return file_names['ecdc_template'] % date_string


def get_ecdc_url(year, month, day):
    base_ul = "https://www.ecdc.europa.eu/sites/default/files/documents"
    url = "%s/%s" % (base_ul, get_ecdc_file(year, month, day))
    return url


def fetch_ecdc(year, month, day):
    url = get_ecdc_url(year, month, day)
    filename = get_ecdc_file(year, month, day)
    filepath = "%s/ecdc/%s" % (data_dir, filename)
    cmd = "wget -O %s %s" % (filepath, url)
    print(cmd)
    os.system(cmd)
    stats = os.stat(filepath)
    file_size = stats.st_size
    if file_size == 0:
        print('File is empty')
        os.unlink(filepath)
        return False

    convert_ecdc_to_csv(filepath)
    return True


def convert_ecdc_to_csv(filename):
    filename_csv = filename.replace('.xlsx', '.csv')
    cmd = "xlsx2csv %s > %s" % (filename, filename_csv)
    os.system(cmd)


def fetch_latest_ecdc():
    now = datetime.now()
    result = fetch_ecdc(now.year, now.month, now.day)
    if not result:
        now = now - timedelta(days=1)
        result = fetch_ecdc(now.year, now.month, now.day)

    assert result


def get_latest_ecdc_file():
    files = glob(data_dir+'/ecdc/COVID-19-geographic-dis*.xlsx')
    xlsx_file = sorted(files)[-1]
    file = xlsx_file.replace('.xlsx', '.csv')
    return file


def read_latest_ecdc():
    file = get_latest_ecdc_file()
    raw_data = list(DictReader(open(file, 'r')))
    data = []
    for row in raw_data:
        row = dict(row)
        row['location'] = row['Countries and territories']
        row['cases'] = int(row['Cases'])
        row['deaths'] = int(row['Deaths'])

        if row['location'] == 'United_States_of_America':
            row['location'] = 'US'

        row['date'] = datetime(int(row['Year']), int(row['Month']), int(row['Day']))

        del row['Countries and territories']
        del row['Cases']
        del row['Deaths']
        data.append(row)
    return data


def ecdc_places():
    data = read_latest_ecdc()
    return sorted({d['location'] for d in data})


def get_ecdc_data(location='US', field='cases'):
    if location not in ecdc_places():
        print('location: %s not in list of locations\n' % location)
        print(ecdc_places())

    data = [i for i in read_latest_ecdc() if i['location'] == location]
    data = sorted(data, key=lambda x: x['date'])
    dates = [i['date'] for i in data]
    number = [i[field] for i in data]
    return dates, number


if __name__ == "__main__":
    fetch_latest_ecdc()
