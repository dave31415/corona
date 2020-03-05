from app import app
from corona.read_data import read_jh_data
from corona.plotting import plot

data = read_jh_data()

@app.route('/')
@app.route('/index')
def index():
    try:
        return plot(data, delta=True, raw_html=True)
    except ValueError as err:
        return "Hello worlds! Error trying to plot data %s" % valError