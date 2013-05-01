import json
import sqlite3


class Channel:

    def __init__(self, slug):
        self._slug = slug
        _conn = sqlite3.connect('relnotes.sqlite')
        for row in _conn.execute('SELECT id FROM Channels '
                                 'WHERE channel_name=? LIMIT 1',
                                 (self.name,)):
            (self._idee,) = row or (None,)

    @property
    def json(self):
        return json.dumps(self.data)

    @property
    def data(self):
        return {
            'name': self.name,
            'id': self.idee,
        }

    @property
    def name(self):
        #TODO: put slugs in the db
        if (self._slug is 'esr'):
            return 'ESR'
        else:
            return self._slug.capitalize()

    # idee b/c id is taken
    @property
    def idee(self):
        return self._idee

    @property
    def slug(self):
        return self.name.lower()
