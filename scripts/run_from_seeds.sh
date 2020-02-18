#!/usr/bin/env bash

set -eu -o pipefail

# === CONFIGURATION TODO

# path to the root of the swisstext-project. Here, assuming we launch from the root
ROOT_PATH=$PWD
# path to the venv to use
VENV_PATH="$ROOT_PATH/venv"
# mongo db name
DB=XX
# config for swisscrawl
CONFIG="$ROOT_PATH/config/prod_config.yaml"
# seed file (default: find a text file starting with seeds_)
SEED_FILE=$(echo "seeds_"*".txt")
# prefix for the log file. Will generate two .log: $LOG_FILE_PREFIX-scrape.log, $LOG_FILE_PREFIX-search.log
LOG_FILE_PREFIX=expXX_experiment-
# number of bootstrap URLs per iteration
N_BOOTSTRAP_URLS_PER_ITERS=200

if [ ! -f "$SEED_FILE" ]; then
    echo "$SEED_FILE doesn't exist. Quitting"
    exit 1
fi

# === set the venv and export some variables

source "$VENV_PATH/bin/activate"
export PYTHONPATH="$ROOT_PATH:$ROOT_PATH/src"
export PYTHONUNBUFFERED=1

# check st_scrape is available
st_scrape >& /dev/null
[ $? -ne 0 ] && echo "st_scrape not found" && exit 1

# == prepare db

# mongo $DB --quiet --eval "db.dropDatabase()"
# HERE, either copy the old database OR bootstrap a new one...
#   INIT: mongo $DB --eval 'db.users.insert({ "_id" : "swisscom", "password" : "f0317c02806a7a326746b8dd4104d57d", "roles" : [ "admin" ] })'
#   COPY: mongorestore -d $DB $INITIAL_DUMP

# == run search

echo -e "@@ Running search...\n"
time (st_search -d $DB -c prod_config.yaml -l debug from_file $SEED_FILE) |& tee -a $LOG_FILE_PREFIX-search.log

# == get number of URLs

num_urls=$(tail $LOG_FILE_PREFIX-search.log | grep -Po 'Found [0-9]+ new URLs' | sed 's/[^0-9]//g')
echo "Got $num_urls URLs."

# == run scrape

echo -e "\n@@ Running scrape"
N=$N_BOOTSTRAP_URLS_PER_ITERS

# Compute the number of iterations (and URLs per iteration) required to "consume" all URLs found during search.
# We ideally want ~200 bootstrap URLs per iter.
#   478 URLs => $iters="200 278"
#   525 URLs => $iters="200 200 125"
iters=$(python <<EOF
iters = [$N] * ($num_urls // $N)
remainder = $num_urls % $N
if remainder < $N // 2:
   iters[-1] += remainder
else:
    iters.append(remainder)
print(' '.join(map(str, iters)))
EOF
)

echo -e "  iterations: $(echo $iters)\n"
i=0
for n in ${iters}; do
    echo -e "\n===== ITER $i (n=$n) =====\n" | tee -a $LOG_FILE_PREFIX-scrape.log
    (time st_scrape -d $DB -c "$CONFIG" -l info from_mongo --what ext -n $n) |& tee -a $LOG_FILE_PREFIX-scrape.log
    i=$(( $i + 1 ))
done