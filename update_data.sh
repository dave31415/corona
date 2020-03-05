rm -rf tmp_download
rm -rf data/updates

mkdir -p tmp_download

wget -O tmp_download/tmp_master.zip https://github.com/CSSEGISandData/COVID-19/archive/master.zip
cd tmp_download
unzip tmp_master.zip
rm tmp_master.zip
cd ..
mkdir data/updates

cp tmp_download/COVID-19-master/csse_covid_19_data/csse_covid_19_daily_reports/* data/updates
rm -rf tmp_download
echo Update complete
echo `ls -ltr data/updates/*.csv | wc -l` data files
