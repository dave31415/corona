from csv import DictReader
from glob import glob
from datetime import datetime
from datetime import timedelta
import os
from bs4 import BeautifulSoup
from html_table_extractor.extractor import Extractor

from corona.file_names import file_names, data_dir, world_o_meter_dir


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
        row['location'] = row['countriesAndTerritories']
        row['cases'] = int(row['cases'])
        if row['deaths'] == '':
            row['deaths'] = 0

        row['deaths'] = int(row['deaths'])

        if row['location'] == 'United_States_of_America':
            row['location'] = 'US'

        row['date'] = datetime(int(row['year']), int(row['month']), int(row['day']))

        del row['countriesAndTerritories']
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


def read_open_table():
    return list(DictReader(open(file_names['open_table'], 'r')))


def read_states():
    states = list(DictReader(open(file_names['states'], 'r')))
    return [i['State'] for i in states]


def read_state_vote():
    states = list(DictReader(open(file_names['states'], 'r')))
    return {i['State']: float(i['Gov_R']) for i in states}


def get_open_table_for_states():
    ot = read_open_table()
    states = read_states()
    return {i['Name']: i for i in ot if i['Type'] == 'state'
            and i['Name'] in states}


def read_world_o_meter_raw(date_time_string):
    if 'html' not in date_time_string:
        filename = file_names['world_o_meter'].format(date=date_time_string)
    else:
        filename = date_time_string

    return open(filename, 'r').read()


def cap_state(state):
    return " ".join([i.capitalize() for i in state.split()])


def line_to_num(line):
    return int(line.split('>')[1].split('<')[0].strip().replace(',', ''))


def get_world_o_meter_values(date_time_string):
    html = read_world_o_meter_raw(date_time_string)
    if len(html) < 100:
        return None

    states = read_states()
    states.append('Puerto Rico')

    soup = BeautifulSoup(html, 'html.parser')

    extractor_today = Extractor(soup, id_="usa_table_countries_today")
    extractor_today.parse()
    table_today = extractor_today.return_list()

    extractor_yest = Extractor(soup, id_="usa_table_countries_yesterday")
    extractor_yest.parse()
    table_yest = extractor_yest.return_list()

    data = {}
    new_today = None
    new_yest = None

    for state in states:
        today = 0
        yesterday = 0

        for row in table_today:
            if cap_state(state).strip() == row[0].strip():
                today = int(row[1].replace(',', ''))

                new_today = row[2].strip().replace(',', '').replace('+', '')
                if new_today == '':
                    new_today = 0
                else:
                    new_today = int(new_today)

        for row in table_yest:
            if cap_state(state).strip() == row[0].strip():
                yesterday = int(row[1].replace(',', ''))

                new_yest = row[2].strip().replace(',', '').replace('+', '')
                if new_yest == '':
                    new_yest = 0
                else:
                    new_yest = int(new_yest)

        assert yesterday > 0
        assert today > 0

        diff = today - yesterday
        assert diff < 10000

        data[state] = {'total_cases_yesterday': yesterday,
                       'total_cases_today': today,
                       'difference': diff,
                       'new_today': new_today,
                       'new_yesterday': new_yest}

        assert new_today == diff

    return data


def get_datetime_from_filename(filename):
    datetime_string = filename.split('/')[-1].split('report_')[-1].split('.html')[0]
    date_time_obj = datetime.strptime(datetime_string, '%y-%m-%d_%H:%M:%S')
    return date_time_obj


def get_sequences():
    files = sorted(glob(world_o_meter_dir+'/*.html'))
    n_files = len(files)
    print(n_files, 'files')
    states = read_states()
    states.append('Puerto Rico')
    seq_data = {state: [] for state in states}

    date_time = []
    for file in files:
        date_time.append(get_datetime_from_filename(file))
        data = get_world_o_meter_values(file)
        if data is None:
            continue

        for state in states:
            n_cases = data[state]['new_today']
            seq_data[state].append(n_cases)

    return date_time, seq_data


if __name__ == "__main__":
    fetch_latest_ecdc()
