# corona
Coronavirus COVID-19 data and analysis tools

Clone repo
./install.sh

Get or update the data
source update_data.sh

ipython

from corona.read_data import read_jh_data
data = read_jh_data()

from corona.plotting import plot

# plot all the data for all regions. Shows cases, recovered and deaths in cumulative numbers        

plot(data)
 
![alt text](https://raw.githubusercontent.com/dave31415/corona/master/images/all_data.png)

# look at day to day changes
plot(data, delta=True)

# lets make selections
from corona.selector import Selector
            
# Just Mainland China
s=Selector(country='Mainland China')
plot(data, delta=True, selector=s)

# Just Mainland China, Guangdong province
s=Selector(country='Mainland China', province='Guangdong')
plot(data, delta=True, selector=s)
![alt text](https://raw.githubusercontent.com/dave31415/corona/master/images/guangdong.png)


# Just Mainland China, not Hubei province
s=Selector(country='Mainland China', province='!Hubei')
plot(data, delta=True, selector=s)

# Just United States patients evaculated from the Diamond Princess ship. Shows ability to use an arbitrary function for selection
s = (country='US', filter=lambda x: "Diamond" in x['province'])
plot(data, selector=s, title='US Diamond Princess')

# Show me all the countries
from corona.read_data import get_countries
get_countries()

# Show me all the country regions
from corona.read_data import get_countries
get_countries(province=True)

s=Selector(province="Sacramento County, CA")
plot(data, selector=s)
