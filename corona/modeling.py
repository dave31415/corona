import numpy as np
from bokeh.plotting import figure, show


def get_params():
    return {'death_rate_initial': 0.02,
            'sampling_efficiency': 0.5,
            'infection_rate_initial': 3.0,
            'infection_rate_final': 0.7,
            'infection_rate_time_scale_days': 120.0,
            'n_days_spread': 10,
            'healing_delay_days': 10,
            'death_delay_days': 10,
            'num_initial': 100}


def simulate(n_days, params=None, y_log=False):
    y_axis_type = "linear"
    if y_log:
        y_axis_type = "log"

    if params is None:
        params = get_params()
    r0 = params['infection_rate_initial']
    r_final = params['infection_rate_final']

    tau = params['infection_rate_time_scale_days']
    cases = [params['num_initial']]
    deaths = [0]
    healed = [0]
    new_cases_list = [0]

    for day in range(1, n_days):
        cases_now = cases[-1]
        weight = np.exp(-day/tau)
        death_rate = params['death_rate_initial']

        r0_effective = weight * r0 + (1 - weight) * r_final

        r_daily = (1 + r0_effective) ** (1.0 / params['n_days_spread']) - 1
        print(r_daily)
        new_cases = cases_now * r_daily

        if day >= params['healing_delay_days']:
            new_healed = new_cases_list[-params['healing_delay_days']] * (1-death_rate)
        else:
            new_healed = 0.0

        if day >= params['death_delay_days']:
            new_deaths = new_cases_list[-params['death_delay_days']] * death_rate
        else:
            new_deaths = 0.0

        new_cases_list.append(new_cases)
        net_new_cases = new_cases - new_healed - new_deaths

        deaths.append(new_deaths)
        healed.append(new_healed)

        vals = (cases_now, r0_effective, new_cases, new_deaths, new_healed, net_new_cases)

        print("cases=%0.1f, r0_eff=%0.3f, new=%0.1f, deaths=%0.1f, healed=%0.1f, net_new=%0.1f" % vals)
        cases_update = max(0, cases_now + net_new_cases)
        cases.append(cases_update)

    days = np.arange(n_days)
    fig = figure(y_axis_type=y_axis_type)
    fig.line(days, cases, legend_label='cases', color='blue')
    fig.line(days, healed, legend_label='recovered', color='green')
    fig.line(days, deaths, legend_label='deaths', color='red')
    show(fig)

    length_epidemic = sum([i > 1 for i in deaths])
    tot_deaths = sum(deaths)
    tot_cases = sum(new_cases_list)

    print('Total cases: %0.1f' % tot_cases)
    print('Total deaths: %0.1f' % tot_deaths)
    print('Length of epidemic: %0.1f days' % length_epidemic)

    print('Total deaths (thousands): %0.1f' % (tot_deaths/1000.0))

    return cases, deaths, healed
