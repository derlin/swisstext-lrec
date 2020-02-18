import logging

from seeding.generator_base import GeneratorBase

logger = logging.getLogger('generator-ngr')


class NgramGenerator(GeneratorBase):

    def generate_seeds(self, freqs, n=100, proba_threshold=0.95,
                       max_deu=None, max_eng=None, **kwargs):
        seeds = []
        logger.info(f'Generating trigram seeds: n={n}, pt={proba_threshold}')

        for seed in freqs.sort_values('cnt', ascending=False).word.values:
            proba = self.lid.predict([seed])[0]
            if proba > 0.95:
                seeds.append(seed)
            logger.info(f'  {"x" if proba < .95 else " "} {seed:40s} {proba * 100:.2f}')
            if len(seeds) >= n:
                break

        return seeds


if __name__ == '__main__':
    import argparse, sys

    parser = argparse.ArgumentParser()
    NgramGenerator.register_input_args(parser)
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), default=sys.stdout,
                        help='Output file (default stdout).')
    parser.add_argument('-n', '--num-seeds', default=10, type=int, help='Number of seeds to generate.')
    parser.add_argument('-w', '--ngram-range', nargs=2, type=int, default=(3, 3), help='Number of words per seed.')
    parser.add_argument('-p', '--min-proba', default=0.95, help='Min. GSW probability for a seed to be accepted.')
    parser.add_argument('--quiet', action='store_true', help='Be quiet')
    args = parser.parse_args()

    if not args.quiet:
        logging.basicConfig(level=logging.ERROR, format='%(msg)s')
        logging.getLogger('generator').setLevel(logging.INFO)
        logging.getLogger('generator-ngr').setLevel(logging.INFO)

        print('Using arguments:')
        print('\n'.join(f'  {k}={v}' for k, v in vars(args).items()))
        print()

    generator = NgramGenerator()
    # get sentences
    sentences = generator.load_sentences(args)
    # get ngram frequencies
    freqs = generator.compute_freqs(sentences, ngram_range=args.ngram_range)
    # filter out ngrams with too many eng/german words
    max_german_words = args.ngram_range[0] // 2
    generator.filter_freqs(freqs, min_freq=2, max_deu_words=max_german_words, max_eng_words=0)
    # generate seeds
    seeds = generator.generate_seeds(freqs, n=args.num_seeds, proba_threshold=args.min_proba)
    # write
    args.output.write('\n'.join(seeds))
