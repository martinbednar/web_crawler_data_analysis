# Web crawler - Data analysis
 
The scripts in this repository are used to analyze data obtained while crawling the web using the tool [Web Crawler](https://github.com/martinbednar/web_crawler).

Already crawled data, which can be analyzed using scripts in this repository, is published on [the FIT cloud](https://nextcloud.fit.vutbr.cz/s/oCdMmJi45oaC2M3).

The results from the previous crawling are also published on [the FIT cloud](https://nextcloud.fit.vutbr.cz/s/3nbB4iaQ7PcrFAM).

## Get results from crawling for FingerPrint Detector

FingerPrint Detector (first published in version 0.6 of [JShelter](https://github.com/polcak/jsrestrictor)) needs a JSON configuration file with JavaScript endpoints and their weights,
where weight means how much this endpoint is abused to get a device fingerprint.

The results (endpoints + their weights) can be obtained from the crawled data by runnning the Python script `fpd_get_results.py`. This script expects the following parameters:
* --dbs <the path to the folder where the SQLite databases containing captured javascript calls are stored>
* --dbs_uMatrix <the path to the folder where the SQLite databases containing captured javascript calls with uMatrix are stored>
* --dbs_uBlock <the path to the folder where the SQLite databases containing captured javascript calls with uBlock Origin are stored>

The output will be saved in the `./results` directory.

The output will look like [these results](https://nextcloud.fit.vutbr.cz/s/GjkTJzweccgxw6n).

## Comprehensive analysis of crawled data

Much more information can be mined from the crawled data than just the endpoints and their weights. The Python script `start_analysis.py` is here for a comprehensive analysis of the crawled data.

This script `start_analysis.py` expects following parameters:
* --dbs <the path to the folder where the SQLite databases containing captured javascript calls are stored>
* --dbs_p <the path to the folder where the SQLite databases containing captured javascript calls with a privacy extension (e.g. uBlock Origin) are stored>

The output will be saved in the `./results` directory.

The output will look like [these results](https://nextcloud.fit.vutbr.cz/s/xDfSAe3Nx7iFSm4).
