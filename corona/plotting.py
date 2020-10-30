from bokeh.embed import file_html
from bokeh.resources import CDN
from collections import Counter
from bokeh.plotting import figure, show
from bokeh.io import output_file
import numpy as np
from datetime import datetime
from corona.selector import Selector
from corona.read_data import get_ecdc_data, get_open_table_for_states, read_jh_data, read_state_vote
from corona.fit_spline import trend_filter
from corona.read_data import get_sequences

cuts = [-100, -98, -88, -78, -68, -64, -20]


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


def get_change(jh_data, field, selector=None, n_weeks=3):
    dates, counts = get_counts_by_country(jh_data, field, selector=selector)
    counts = get_diff(counts)
    offset_days = n_weeks * 7
    after = counts[-1]
    before = counts[-1 - offset_days]
    return before, after


def get_open_table_statistics(date_string):
    open_table_data = get_open_table_for_states()
    states = open_table_data.keys()
    return {state: float(open_table_data[state][date_string]) for state in states}


def get_open_table_v_change():
    date = '6/1'
    n_weeks = 3
    n_min = 100
    jh_data = read_jh_data()
    open_table_stats = get_open_table_statistics(date)
    data = {}
    for state in open_table_stats.keys():
        s = Selector(country='US', province=state)
        ot_stat = open_table_stats[state]
        before, after = get_change(jh_data, 'confirmed', selector=s, n_weeks=n_weeks)
        if before < n_min:
            continue

        change = 100.0*(after/before - 1)
        data[state] = {'state': state,
                       'open_table_decline': ot_stat,
                       'case_change': change,
                       'before': before,
                       'after': after}

    n_states = len(data)
    print('n_states: %s' % n_states)

    return data


def get_ot_stats():
    data = get_open_table_v_change()
    plot_open_table_v_change(data)

    #cuts = [-100, -98, -96, -85, -65, -20]

    rows = data.values()
    rows = sorted(rows, key=lambda k: k['open_table_decline'])

    states = np.array([r['state'] for r in rows])
    x = np.array([r['open_table_decline'] for r in rows])
    y = np.array([r['case_change'] for r in rows])
    b = np.array([r['before'] for r in rows])
    a = np.array([r['after'] for r in rows])

    x_data = []
    y_data = []
    v_data = []

    print('Groupings in order')

    vote = read_state_vote()

    for i in range(len(cuts)-1):
        start = cuts[i]
        fin = cuts[i+1]
        w = np.where((x >= start) & (x < fin))[0]
        xx = x[w]
        yy = y[w]
        bb = b[w]
        aa = a[w]
        states_in_bin = states[w]
        votes = np.array([vote[s] for s in states_in_bin])
        mean_vote = 100 * votes.mean()
        mean_decline = round(xx.mean())
        mean_change = round(yy.mean())
        sum_before = bb.sum()
        sum_after = aa.sum()
        change_total = round(100.0 * (sum_after / sum_before - 1))

        # print(start, fin, mean_decline, mean_change, sum_before, sum_after, change_total)
        print(sorted(states_in_bin))
        x_data.append(mean_decline)
        y_data.append(change_total)
        v_data.append(mean_vote)

    title = "US States: Opening restaurants correlation with COVID-19 cases"

    output_file('binned.html')

    fig = figure(width=900, height=700, title=title,
                 x_axis_label='YoY change in Open Table seatings on June 1 (%)',
                 y_axis_label='3 week change in COVID-19 cases (%)')

    fig.circle(x_data, y_data, size=12)
    fig.line(x_data, y_data, line_width=3)
    fig.xaxis.axis_label_text_font_size = '18pt'
    fig.yaxis.axis_label_text_font_size = '18pt'

    fig.xaxis.major_label_text_font_size = "14pt"
    fig.yaxis.major_label_text_font_size = "14pt"
    fig.title.text_font_size = "16pt"

    fig.line(x_data, v_data, color='red', line_dash='dashed')
    fig.circle(x_data, v_data, color='red', size=6)
    show(fig)


def plot_open_table_v_change(data):
    fig = figure(width=900, height=700, x_range=(-100, -50))
    rows = data.values()
    rows = sorted(rows, key=lambda k: k['open_table_decline'])

    x = [r['open_table_decline'] for r in rows]
    y = [r['case_change'] for r in rows]

    fig.circle(x, y)

    for cut in cuts:
        fig.line([cut, cut], [-100, 1000], color='green', alpha=0.4)

    show(fig)
    for row in rows:
        print(row)


def get_diff(counts):
    counts_padded = [0] + list(counts)
    diff = []
    for i in range(1, len(counts_padded)):
        diff.append(counts_padded[i] - counts_padded[i-1])
    return diff


def plot(jh_data, selector=None, delta=False, title=None, y_log=False, raw_html=False, field=None):
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

    if field is not None:
        fields = [(field, 'black')]

    for field, color in fields:
        dates, counts = get_counts_by_country(jh_data, field, selector=selector)

        if delta:
            counts = get_diff(counts)
        fig.line(dates, counts, legend_label=field, color=color, line_width=3)
        fig.circle(dates, counts, alpha=0.2, color=color)

    dates, deaths = np.array(get_counts_by_country(jh_data, 'deaths', selector=selector))
    dates, confirmed = np.array(get_counts_by_country(jh_data, 'confirmed', selector=selector))
    death_rate = 100 * 1000 * deaths/(confirmed + 0.0001)

    # fig.line(dates, death_rate, legend_label='death rate (%)/1000', color='gray', line_width=2)
    print(dates)

    fig.legend.location = "top_left"
    
    if not raw_html:
        show(fig)
    else:
        return file_html(fig, CDN)


def plot_ecdc(location='US', field='cases', y_log=False,
              date_min=None, date_max='2050-01-01',
              degree=1, show_fit=False, show_smooth=False,
              fudge=None):

    if fudge is None:
        if location == 'Italy':
            fudge = {'2020-03-15': 90 + 3000, '2020-03-16': 6230 - 3000}

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
    number_7 = seven_day_ma(number)

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
    fig.line(date, number_7, color='purple')

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


def seven_day_ma(y):
    n = len(y)

    y_smooth = y * 1.0

    for i in range(n):
        if i > 0:
            y_smooth[i] = np.mean(y[max(0, i-7): i])

    return y_smooth


def plot_day():
    date_time, data = get_sequences()
    plot_seq(date_time, data)


def plot_seq(date_time, data, state=None):
    arrays = [np.array(i) for i in data.values()]
    if state is None:
        total = sum(arrays)
        title = 'All states'
    else:
        total = data[state]
        title = state

    fig = figure(x_axis_type='datetime', title=title)
    fig.line(date_time, total)
    fig.circle(date_time, total)
    show(fig)
