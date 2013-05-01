import json
import sqlite3


class Product:

    def __init__(self, slug):
        self._slug = slug
        _conn = sqlite3.connect('relnotes.sqlite')
        for row in _conn.execute('SELECT id, product_text '
                                 'FROM Products '
                                 'WHERE product_name=? LIMIT 1',
                                 (self.name,)):
            (self._idee, self._text) = row or (None, None)

    @property
    def alt_product(self):
        alt_product_map = {
            'mobile': 'firefox',
            'firefox': 'mobile',
            'esr': ''
        }
        return alt_product_map[self.slug]

    @property
    def slug(self):
        return self._slug

    @property
    def name(self):
        #TODO: put slugs in the db
        name_map = {
            'mobile': 'Firefox for mobile',
            'firefox': 'Firefox',
            'esr': 'Firefox ESR'
        }
        return name_map[self.slug]

    @property
    def json(self):
        return json.dumps(self.data)

    @property
    def data(self):
        return {
            'name': self.name,
            'slug': self.slug,
            'id': self.idee,
            'text': self.text,
            'alt_product': self.alt_product
        }

    @property
    def text(self):
        return self._text

    # idee b/c id is taken
    @property
    def idee(self):
        return self._idee
