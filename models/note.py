import json


class Note:

    def __init__(self, **kwargs):
        # create an unknown set of private fields
        for key in kwargs.keys():
            k = "_" + key
            kwargs[k] = kwargs[key]
            del kwargs[key]

        self.__dict__.update(kwargs)

    @property
    def json(self):
        return json.dumps(self.data)

    @property
    def data(self):
        return {
            'type': self.tipe,
            'tag': self.tag,
            'description': self.description,
            'bug': self.bug,
            'first_in': self.first_in,
            'fixed_in_version': self.fixed_in_version,
            'fixed_in_channel': self.fixed_in_channel
        }

    # tipe b/c type is taken
    @property
    def tipe(self):
        if (hasattr(self, '_tipe')):
            return self._tipe

    @property
    def description(self):
        if (hasattr(self, '_description')):
            return self._description

    @property
    def tag(self):
        if (hasattr(self, '_tag')):
            return self._tag
        else:
            return self.tipe.upper()

    @property
    def bug(self):
        if (hasattr(self, '_bug')):
            return self._bug

    @property
    def first_in(self):
        if (hasattr(self, '_first_in')):
            return self._first_in

    @property
    def fixed_in_version(self):
        if (hasattr(self, '_fixed_in_version')):
            return self._fixed_in_version

    @property
    def fixed_in_channel(self):
        if (hasattr(self, '_fixed_in_channel')):
            return self._fixed_in_channel
