from corona.read_data import read_jh_data
from corona.plotting import plot

# This script is being used as a scratch pad in order to develop 
# against the DS package

data = read_jh_data()

raw_html = plot(data, delta=True, raw_html=True)

print("Raw Html %s", raw_html)