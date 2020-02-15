import logging

import numpy as np

from seeding.generator_base import GeneratorBase

logger = logging.getLogger('generator-rnd')


class RandomGenerator(GeneratorBase):

    def generate_seeds(self, freqs, n=100, num_words=(3,), random_seed=1984424,
                       proba_threshold=0.95, max_one_char_words=2, **kwargs):
        np.random.seed(random_seed) # reproducibility

        logger.info(f'Generating random seeds: n={n}, num_words={num_words}, seed={random_seed}, pt={proba_threshold} ')
        seeds = []

        # == do the work
        while len(seeds) < n:
            nw = np.random.choice(num_words)
            ws = freqs.sample(nw, weights=freqs.cnt).word.values.tolist()
            seed = ' '.join(ws)
            if sum(len(w) == 1 for w in ws) >= max_one_char_words:
                logger.info(f'  x {seed:40s} zu kurz')
                continue

            proba = self.lid.predict([seed])[0]
            if proba > proba_threshold:
                seeds.append(seed)
            logger.info(f'  {"x" if proba < .95 else " "} {seed:40s} {proba * 100:.2f}')

        return seeds


if __name__ == '__main__':
    import argparse, sys

    parser = argparse.ArgumentParser()
    RandomGenerator.register_input_args(parser)
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), default=sys.stdout,
                        help='Output file (default stdout).')
    parser.add_argument('-n', '--num-seeds', type=int, default=10, help='Number of seeds to generate.')
    parser.add_argument('-w', '--num-words', nargs='+', type=int, default=(3,),
                        help='Number of words per seed (random sample).')
    parser.add_argument('-p', '--min-proba', default=0.95, help='Min. GSW probability for a seed to be accepted.')
    parser.add_argument('--quiet', action='store_true', help='Be quiet')
    args = parser.parse_args()

    if not args.quiet:
        logging.basicConfig(level=logging.ERROR, format='%(msg)s')
        logging.getLogger('generator').setLevel(logging.INFO)
        logging.getLogger('generator-rnd').setLevel(logging.INFO)

    generator = RandomGenerator()
    # get sentences
    sentences = generator.load_sentences(args)
    # get word frequencies
    freqs = generator.compute_freqs(sentences)
    # filter out words with too many eng/german words
    freqs = generator.filter_freqs(freqs)
    # generate seeds
    max_one_char_words = min(args.num_words) // 2
    seeds = generator.generate_seeds(
        freqs, n=args.num_seeds, num_words=args.num_words, random_seed=args.random_seed, proba_threshold=args.min_proba)
    # write
    args.output.write('\n'.join(seeds))
