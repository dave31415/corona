class Selector:
    def __init__(self, **kwargs):
        if 'filter' in kwargs:
            self.filter_func = kwargs['filter']

            del kwargs['filter']
            self.filtered=True
        else:
            self.filter_func = lambda x: True
            self.filtered = False

        self.filter_dict = kwargs

    def __call__(self, record):
        for key, val in self.filter_dict.items():
            if val.startswith('!'):
                val = val[1:].strip()
                if val in record[key]:
                    return False
            else:
                if val not in record[key]:
                    return False

        return self.filter_func(record)

    def get_title(self):
        title = ''
        adds = []
        for key, val in self.filter_dict.items():
            adds.append("%s=%s" % (key, val))

        if len(adds) > 0:
            title += ', '.join(adds)

        if self.filtered:
            # not sure how to make this into an
            # informative title, just say filtered for now
            title += ' - filtered'

        return title
