#!/usr/bin/env zsh

set -eu -o pipefail

if [ -z "$1" ]; then
    echo "Usage $0 <dbname>"
    exit 1
fi

DB=$1
ROOT_PATH="$PWD"
CONFIG="$ROOT_PATH/config/prod_config.yaml"
LOG=st-scrape-iter.log
VENV_PATH="$ROOT_PATH/venv"

ITER=50
URLS_PER_ITERS=200
HOW=random

# source and export
source "$VENV_PATH/bin/activate"
export PYTHONPATH="$ROOT_PATH:$ROOT_PATH/src"
export PYTHONUNBUFFERED=1

# check st_scrape is available
st_scrape >& /dev/null
[ $? -ne 0 ] && echo "st_scrape not found" && exit 1

echo "starting iterations" > $LOG
echo "  Using db $DB" > $LOG
echo "  Number of iters: ITER=$ITER" > $LOG
echo "  Number of pulled URLs per iter: URLS_PER_ITERS=$URLS_PER_ITERS" > $LOG
echo "  Type of URLs pulled: HOW=$HOW" > $LOG

for i in {1..$ITER}; do
    echo -e "\n===== ITER $i =====\n" | tee -a $LOG
    (time st_scrape -c "$CONFIG" --db $DB -l info from_mongo --what new --how $HOW -n $URLS_PER_ITERS) |& tee -a $LOG
done