"""
Keep all filename/path logic here rather than polluting code with hardcoded paths
"""
import os

data_dir_default = 'data'
tmp_dir = 'tmp'

data_dir = os.getenv('CORONA_DATA_DIR', data_dir_default)
novel_dir = "%s/novel" % data_dir
jh_dir = "%s/jh/COVID-19-master_2020_03_03/csse_covid_19_data/csse_covid_19_daily_reports" % data_dir


file_names = {'ts_data': "%s/COVID19_open_line_list.csv" % novel_dir,
              'jh_dir': jh_dir,
              'tmp_dir': tmp_dir,
              'jh_tmp_dir': "%s/jh_data_dump" % jh_dir,
              'jh_sub_dir': "COVID-19-master/csse_covid_19_data/csse_covid_19_daily_reports",
              'jh_dir_update': "%s/updates" % data_dir,
              'ecdc_template': 'COVID-19-geographic-disbtribution-worldwide-%s.xlsx'}

# the above spelling error "disbtribution" is intended
