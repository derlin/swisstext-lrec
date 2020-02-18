import logging
import os
import random
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from bert_lid import BertLid
from sklearn.feature_extraction.text import CountVectorizer

logger = logging.getLogger('generator')


# === superclass

class GeneratorBase(ABC):

    def __init__(self):
        dico_path_format = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dict_{}.txt')

        with open(dico_path_format.format('eng')) as f:
            self.english_dict = set([w.strip() for w in f])
        with open(dico_path_format.format('deu')) as f:
            self.german_dict = set([w.strip() for w in f])

        self.lid = BertLid()

    def words_in_dict(self, ws, dict):
        return sum(w in dict for w in ws.split(' '))

    def filter_freqs(self, freqs, min_freq=2, max_deu_words=0, max_eng_words=0):
        """
        Filter the ngrams returned by compute_freqs based on German & English words and overall frequency.
        :param freqs: a DataFrame [ngram, freq]
        :param min_freq: the minimum frequency of ngrams to keep (inclusive)
        :param max_deu_words: the maximum number of German words per ngram (inclusive)
        :param max_eng_words: the maximum number of English words per ngram (inclusive)
        :return: the filtered DataFrame
        """
        logger.info(f'Counted {len(freqs)} words/ngrams.')
        logger.info(f'  {(freqs.cnt == 1).sum()} appear only once.')
        words_deu = freqs.word.apply(lambda s: self.words_in_dict(s, self.german_dict))
        words_eng = freqs.word.apply(lambda s: self.words_in_dict(s, self.english_dict))
        logger.info(f'  words/ngrams with deu words: {(words_deu > 0).sum()}, with eng words: {(words_eng > 0).sum()}')
        logger.info(
            f'  filtering using max_deu_words={max_deu_words}, max_english_words={max_eng_words}, min_freq={min_freq}')
        freqs = freqs[(freqs.cnt >= min_freq) & (words_deu <= max_deu_words) & (words_eng <= max_eng_words)]
        logger.info(f'Final count: {len(freqs)}')
        return freqs

    @abstractmethod
    def generate_seeds(self, sentences, n=100, **kwargs):
        pass

    @staticmethod
    def compute_freqs(sentences, token_pattern='[^\W|\d]+', lowercase=True, **kwargs):
        """
        Count and return the frequency of words from a list of sentences.
        To compute the frequency of ngrams, just pass ngram_range=(x,y) as a parameter.

        :param sentences: a list of GSW sentences
        :param kwargs: extra parameters passed to the CountVectorizer constructor
        :return: a DataFrame with two columns: word and cnt
        """
        cv = CountVectorizer(token_pattern=token_pattern, lowercase=lowercase, **kwargs)
        cv_fit = cv.fit_transform(sentences)
        return pd.DataFrame(list(zip(
            cv.get_feature_names(),
            np.asarray(cv_fit.sum(axis=0)).squeeze()
        )), columns=['word', 'cnt'])

    @classmethod
    def register_input_args(cls, parser):
        parser.add_argument('-i', '--input', type=str, required=True,
                            help='Either a TXT file containing Swiss German sentences, one per line,'
                                 'or a CSV file (mongo dump) containing columns [text, url, crawl_proba].')
        parser.add_argument('--max-sentences-per-url', type=int, default=1,
                            help='If CSV, keep only X random sentence for each URL (-1 to keep all).')
        parser.add_argument('--min-crawl-proba', type=float, default=0.99,
                            help='If CSV, keep only sentences with a crawl_proba >= X')
        parser.add_argument('--max-sentences', type=int, default=-1,
                            help='keep only X random sentences for generation (-1 to keep all).')
        parser.add_argument('-s', '--random-seed', default=198442, type=int, help='random seed.')

    @classmethod
    def load_sentences(cls, args):
        random.seed(args.random_seed)  # reproducibility

        ext = args.input.split('.')[-1]
        logger.info(f'Loading from {ext} file: {args.input}')

        if ext == 'csv':
            # We have a mongo dump
            df = pd.read_csv(args.input)
            # check the file
            for col in ['text', 'url', 'crawl_proba']:
                assert col in df, f'{args.input}: missing {col} column'

            logger.info(f'  Initial number of sentences: {len(df)}')
            df = df[df.crawl_proba >= args.min_crawl_proba]
            logger.info(f'  Sentences with crawl_proba >= {args.min_crawl_proba}: {len(df)}')
            if args.max_sentences_per_url > 0:
                df = df.sample(frac=1, random_state=args.random_seed) \
                    .groupby('url', group_keys=False).head(args.max_sentences_per_url)
                logger.info(f'  Sampling {args.max_sentences_per_url} sentence per URL.')
            sentences = df.text.values.tolist()

        elif ext == 'txt':
            # we have a file
            with open(args.input) as f:
                sentences = [l.strip() for l in f if len(l.strip())]

        else:
            # unsupported extension...
            raise Exception(f'ERROR: Input file "{args.input}": unknown extension "{ext}"')

        if 0 < args.max_sentences < len(sentences):
            logger.info(f'  Keeping only {args.max_sentences} sentences.')
            sentences = random.sample(sentences, args.max_sentences)

        logger.info(f'Got {len(sentences)} sentences.')

        return sentences
