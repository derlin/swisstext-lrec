#!/usr/bin/env bash

#
# This script exports the sentences of a SwissText Mongo Database running on localhost
# into a CSV file with the columns: text,crawl_proba,url,type,extra,date.
# the file will be named "sentences-{db}.csv" and written in the current directory.
#

if [ -z "$1" ]; then
    echo "Usage $0 <dbname>"
    exit 1
fi

DB=$1

echo "===> running aggregate <==="
mongo $DB <<'EOF'
db.sentences.aggregate([
    {'$lookup':
        {
            'from': 'urls',
            'localField': 'url',
            'foreignField': 'url',
            'as': 'url_info'
        }},
    {'$project':
        {
            'type': {'$arrayElemAt': ['$url_info.source.type', 0]},
            'extra': {'$arrayElemAt': ['$url_info.source.extra', 0]},
            'text': '$text',
            'url': '$url',
            'crawl_proba': '$crawl_proba',
            'date': '$date_added'
        }},
    {'$out': 'results'}
])
EOF

if [ $? -ne 0 ]; then
    echo "something went wrong running aggregate ..."
    exit 1
fi

echo -e "\n===> exporting <==="
mongoexport -d $DB -c results --type csv --fields "text,crawl_proba,url,type,extra,date" > sentences-$DB.csv

echo -e "\n===> cleaning up <==="
mongo $DB --eval 'db.results.drop()'

echo -e '\nDone.'
