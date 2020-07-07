**IMPORTANT** This repository uses [SwissText](https://github.com/derlin/swisstext). The version at the time of publication was `v0.4`. For maintenance purposes, the branch [`lrec`](https://github.com/derlin/swisstext/tree/lrec) will keep the same functionalities, with only minor changes to make the code works with library updates and such.

# SwissText - LREC 

This repository contains the code used to generate [SwissCrawl](https://icosys.ch/swisscrawl),
a corpus of 500,000+ Swiss German (GSW) sentences gathered from crawling the web between September and November 2019.

It uses the [swisstext](https://github.com/derlin/swisstext) crawling pipeline, but has some specific configurations
and tools relative to Swiss German.

# Paper and references

**Paper (LREC, 2019)**: [Automatic Creation of Text Corpora for Low-Resource Languages from the Internet: The Case of Swiss German](https://arxiv.org/abs/1912.00159)

**Citation**:
```bibtex
@article{linder2019automatic,
  title={Automatic Creation of Text Corpora for Low-Resource Languages from the Internet: The Case of Swiss German},
  author={Linder, Lucy and Jungo, Michael and Hennebert, Jean and Musat, Claudiu and Fischer, Andreas},
  journal={arXiv preprint arXiv:1912.00159},
  year={2019}
}
```


# Requirements and notes

* this repo uses **SwissText v0.4**, which is reflected in the **lrec** branch (as shown in the `requirements.txt`). 
  Using a later version may be possible, but I don't guarantee there are no breaking changes...
* ensure you update your pip before installing the requirements: `pip install --upgrade pip`
* a BERT Language ID is required, and you might have to train your own using the procedure and code in https://github.com/derlin/swisstext-bert-lid
* the scripts are assumed to run on a machine having bash
* it is your responsibility to setup a MongoDB database. By default, I assume it runs on localhost using the default port
* the code has been used and tested with **Python 3.6** and was working fine in September, 2019

# Installation

Clone the repo, create a virtualenv and install dependencies:

```bash
# clone this repo
git clone git@github.com:derlin/swisstext-lrec.git
cd swisstext-lrec

# create a virtualenv
python3.6 -m venv venv
source venv/bin/activate

# update pip
pip install --upgrade pip

# install dependencies
pip install -r requirements.txt
```

Once this is done, you should have a commandline tool from `bert_lid` called `bert_lid_install_model`. 
Use it to copy your trained BERT model (again, see https://github.com/derlin/swisstext-bert-lid) to the python lib
folder:

```bash
bert_lid_install_model /path/to/a/model/directory
```

*NOTE:* if you have access to it, the actual LID model used for SwissCrawl is available in
the [models/default](https://gitlab.com/swisscom-gsw/lid/bert-torch-lid/-/tree/master/models/default) folder in GitLab
(model `2019-08-20_leipzig`).

# About the code

## Seeding

NOTE: the code under `src/seeding`, is "optional". 
In order to use it, you need first to add `src` to the python path and to install the `pandas` dependency:

```bash
# given your current directoy is the root of the project
export PYTHONPATH=$PWD/src
# I was using pandas 1.0.1 at the time, so I you have errors, use pip install pandas==1.0.1 instead
pip install pandas
```

### Dictionary sources

**German dictionary**

Option 1:
* download german.7z from https://sourceforge.net/projects/germandict/files
* open the archive
* convert `german.dic` to UTF-8: `iconv -f iso-8859-1 -t utf-8 < german.dic > dict_deu.txt`
* if you have a Swiss German dictionary available, try removing words appearing in it

Option 2:
* look into the `linux-separated-by-country` and play with the options (DE - CH, DE + AT, ...)

**English dictionary**

Taken from http://app.aspell.net/create, using the options shown in the URL below. Script:
```bash
wget -O - http://app.aspell.net/create?max_size=35&spelling=US&max_variant=0&diacritic=strip&special=roman-numerals&download=wordlist&encoding=utf-8&format=inline \
    | grep -E '^\w+$' \
    | sort -f > dict_eng.txt
```

### Seeding scripts

Everything is located under `src/seeding`. The two available tools (to run as commandline scripts) are:

1. `ngram_generator.py`: generate seeds by sampling n-grams from a list of sentences,
2. `random_generator.py`: generate seeds by concatenating X words together.

They correspond to the implementations described in the paper.

# Running an experiment

1. generate some seeds, e.g. `python src/seeding/random_generator.py -i swiss-german-sentences.txt -o seeds.txt`
2. run the searcher, e.g. `st_search -c config/prod_config.yaml from_file seeds.txt`
3. run the scraper, e.g. `st_scrape -c config/prod_config.yaml from_mongo --what ext -n 200` (here: use 200 URLs as starting point)

After generating the seeds, you can also use the script `scripts/run_from_seeds.sh` to automatically search all seeds and 
run the scraper as many times as needed to consume all the new URLs. 
However, don't forget to update the variables at the top of the script before launching 
(and to use a screen session: the runtime is usually hours.)

# License

SwissText Crawler (c) by Lucy Linder

The SwissText Crawler is licensed under a Creative Commons Attribution-NonCommercial 4.0 Unported License.

You should have received a copy of the license along with this work.  
If not, see <http://creativecommons.org/licenses/by-nc/4.0/>.