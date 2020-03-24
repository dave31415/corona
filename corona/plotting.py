from bokeh.embed import file_html
from bokeh.resources import CDN
from collections import Counter
from bokeh.plotting import figure, show
import numpy as np
from datetime import datetime
from corona.selector import Selector
from corona.read_data import get_ecdc_data
from corona.fit_spline import trend_filter


def get_counts_by_country(jh_data, field, selector=None):
    if selector is None:
        selector = Selector()

    count = Counter()
    for record in jh_data:
        if not selector(record):
            continue

        count[record['report_date']] += record[field]

    dates, counts = zip(*sorted(count.items()))
    return dates, counts


def get_diff(counts):
    counts_padded = [0] + list(counts)
    diff = []
    for i in range(1, len(counts_padded)):
        diff.append(counts_padded[i] - counts_padded[i-1])
    return diff


def plot(jh_data, selector=None, delta=False, title=None, y_log=False, raw_html=False):
    if selector is None:
        selector = Selector()

    if title is None:
        title = selector.get_title()

    y_axis_type = "linear"
    if y_log:
        y_axis_type = "log"

    fig = figure(x_axis_type="datetime", title=title, width=800, height=600, y_axis_type=y_axis_type)
    fig.yaxis.axis_label = '# '
    if delta:
        fig.yaxis.axis_label = '# / day'
    else:
        fig.yaxis.axis_label = '# / cumulative'

    fields = [('confirmed', 'blue'),
              ('recovered', 'green'),
              ('deaths', 'red')]
    for field, color in fields:
        dates, counts = get_counts_by_country(jh_data, field, selector=selector)

        if delta:
            counts = get_diff(counts)
        fig.line(dates, counts, legend_label=field, color=color, line_width=3)
        fig.circle(dates, counts, alpha=0.2, color=color)

    dates, deaths = np.array(get_counts_by_country(jh_data, 'deaths', selector=selector))
    dates, confirmed = np.array(get_counts_by_country(jh_data, 'confirmed', selector=selector))
    death_rate = 100 * 1000 * deaths/(confirmed + 0.0001)

    fig.line(dates, death_rate, legend_label='death rate (%)/1000', color='gray', line_width=2)

    fig.legend.location = "top_left"
    
    if not raw_html:
        show(fig)
    else:
        return file_html(fig, CDN)


def plot_ecdc(location='US', field='cases', y_log=False,
              date_min=None, date_max='2050-01-01',
              degree=1, show_fit=False, show_smooth=False,
              fudge=None):
    if y_log:
        y_axis_type = 'log'
    else:
        y_axis_type = 'linear'

    title = location
    fig = figure(x_axis_type="datetime", y_axis_type=y_axis_type,
                 title=title, width=900, height=700, y_axis_label=field)

    fig.yaxis.axis_label_text_font_size = "14pt"

    date, number = get_ecdc_data(location=location, field=field)
    print(number)
    if fudge is not None:
        for k, v in fudge.items():
            year, month, day = k.split('-')
            kk = datetime(int(year), int(month), int(day))
            if kk in date:
                idx = date.index(kk)
                number[idx] = v

    date = np.array(date)
    number = np.array(number)

    if date_min:
        year, month, day = [int(i) for i in date_min.split('-')]
        d_min = datetime(year, month, day)

        year, month, day = [int(i) for i in date_max.split('-')]
        d_max = datetime(year, month, day)

        keep = (date >= d_min) & (date <= d_max)
        date = date[keep]
        number = number[keep]

    fig.circle(date, number)
    fig.line(date, number)

    if show_fit:
        y_fit, doubling_time = poly_fit(number, degree=degree)
        fig.line(date, y_fit, color='red', legend_label='Fit:  doubling every %0.2f days' % doubling_time)
        if show_smooth:
            fig.line(date, smooth(number), color='orange')
        fig.legend.location = 'top_left'
        fig.legend.label_text_font_size = "16pt"

    show(fig)


def smooth(number):
    log_num = np.log(number)
    index = np.arange(len(log_num))
    log_fit = trend_filter(index, log_num, alpha_2=50.0)
    return np.exp(log_fit)


def poly_fit(number, degree=1):
    print(number)
    log_num = np.log(number)
    index = np.arange(len(log_num))
    poly = np.polyfit(index, log_num, degree)
    print('poly')
    print(poly)
    doubling_time = None
    if degree == 1:
        alpha = poly[0]
        growth_rate = 100.0*(np.exp(alpha)-1)
        doubling_time = 1.0/(alpha * np.log2(np.exp(1)))
        print('Daily growth rate: %0.2f percent' % growth_rate)
        print('Doubling time: %0.2f days' % doubling_time)

    log_fit = np.polyval(poly, index)
    return np.exp(log_fit), doubling_time

