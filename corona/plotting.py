from bokeh.plotting import figure, show
from collections import Counter
from corona.selector import Selector


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


def plot(jh_data, selector=None, delta=False, title=None):
    if selector is None:
        selector = Selector()

    if title is None:
        title = selector.get_title()

    fig = figure(x_axis_type="datetime", title=title, width=800, height=600)
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
        fig.line(dates, counts, legend=field, color=color)
        fig.circle(dates, counts, alpha=0.2, color=color)

    fig.legend.location = "top_left"
    show(fig)
