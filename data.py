import numpy as np


class Instance():
    """
    Each line represents a sentence with one complex word annotation and
    relevant information, each separated by a TAB character.
        - The first column shows the HIT ID of the sentence. All sentences with
        the same ID belong to the same HIT.
        - The second column shows the actual sentence where there exists a
        complex phrase annotation.
        - The third and fourth columns display the start and end offsets of the
        target word in this sentence.
        - The fifth column represents the target word.
        - The sixth and seventh columns show the number of native annotators
        and the number of non-native annotators who saw the sentence.
        - The eighth and ninth columns show the number of native annotators and
        the number of non-native annotators who marked the target word as
        difficult.
        - The tenth and eleventh columns show the gold-standard label for the
        binary and probabilistic classification tasks.
    """

    def __init__(self, sentence, test=False):
        self.hit_id = sentence[0]
        self.sentence = sentence[1]
        self.offset = [int(sentence[2]), int(sentence[3])]
        self.target_chars = sentence[4]
        self.annotators = [int(sentence[5]), int(sentence[6])]
        self.tokens, self.target = self.tokenize()
        self.target.sort()
        if not test:
            self.label = [int(sentence[9]), float(sentence[10])]
            self.difficult = [int(sentence[7]), int(sentence[8])]
        else:
            self.label = None
            self.difficult = None

    def __str__(self):
        string = "HIT ID: %s\nSENTENCE: %s\nTOKENS: %s\nOFFSET: %s\nTARGET_CHARS: %s\nTARGET_TOKENS: %s\nANNOTATORS: %s\nDIFFICULT: %s\nLABEL: %s"
        data = (self.hit_id,
                self.sentence,
                self.tokens,
                '%s --> %s' % (self.offset,
                               self.sentence[self.offset[0]:self.offset[1]]),
                self.target_chars,
                '%s --> %s' % (self.target,
                               [self.tokens[i] for i in self.target]),
                self.annotators,
                self.difficult,
                self.label)
        return string % data

    def tokenize(self):
        tokens = []
        target = {}
        endings = ['?', '”', '"', '!', ')', '.']
        start = 0
        for i in range(len(self.sentence)):
            if i in range(self.offset[0], self.offset[1]):
                target[len(tokens)] = True
            if self.sentence[i] == ' ':
                if self.sentence[start:i]:
                    tokens.append(self.sentence[start:i].lower())
                start = i + 1
            elif self.sentence[i] == '\'':
                tokens.append(self.sentence[start:i].lower())
                start = i
            elif self.sentence[i] in (endings + [',', ':', ';', '(', ')', '', '…', '[', ']']):
                if i - start > 0:
                    tokens.append(self.sentence[start:i].lower())
                tokens.append(self.sentence[i:i+1].lower())
                start = i + 1
            elif self.sentence[i] in ['\"', '“']:
                if i - start >= 0:
                    tokens.append(self.sentence[i:i + 1].lower())
                start = i + 1
            if i == len(self.sentence)-1 and self.sentence[i] not in endings:
                tokens.append(self.sentence[start:].lower())
        return tokens, list(target.keys())


class Data():
    """Docstring."""

    def __init__(self, datasets, is_test=False):
        self.instances = []
        self.y = []
        self.y_prob = []
        self.test = is_test
        self.load_data(datasets)

    def load_data(self, datasets):
        for dataset in datasets:
            with open(dataset) as fp:
                lines = [line.split('\t') for line in fp.read().splitlines()]
            # assert data consistance
            for line in lines:
                if not self.test:
                    assert len(line) == 11, "Missing field: %s" % line
                else:
                    assert len(line) == 7, "Missing field: %s" % line
            # create instances
            for line in lines:
                self.instances.append(Instance(line, test=self.test))
        if not self.test:
            self.y = np.array([instance.label[0] for instance in self.instances])
            self.y_prob = np.array([instance.label[1] for instance in self.instances])

    def statistics(self):
        print('Instances: %d' % len(self.instances))
        unique_insts = len(set([i.hit_id for i in self.instances]))
        unique_targets = len(set([i.target_chars for i in self.instances]))
        sents_len = [len(i.sentence) for i in self.instances]
        tokens_len = [len(i.tokens) for i in self.instances]
        print('Unique instances: %d' % unique_insts)
        print('Unique targets: %d' % unique_targets)
        print('Sentences char length: %.2f (±%.2f)' % (np.mean(sents_len),
                                                       np.std(sents_len)))
        print('Sentences token length: %.2f (±%.2f)' % (np.mean(tokens_len),
                                                        np.std(tokens_len)))


if __name__ == "__main__":
    training_data = ['datasets/english/News_Train.tsv',
                     'datasets/english/WikiNews_Train.tsv',
                     'datasets/english/Wikipedia_Train.tsv',
                     ]
    data = Data()
    data.load_data(training_data)
    print('=====STATISTICS=====')
    data.statistics()
    print('=====EXAMPLE=====')
    # print(data.instances[0])
    # print(data.instances[10])
    # print(data.instances[20])
    # print(data.instances[30])
    # print(data.instances[60])
    # print(data.instances[70])
    # print(data.instances[80])
    # print(data.instances[90])
    # print(data.instances[8283])
