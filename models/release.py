import json
import sqlite3

from datetime import datetime

from models.channel import Channel
from models.note import Note
from models.product import Product


class Release:

    def __init__(self, product_name, channel_name, options):

        #initialize properties
        self.product = Product(product_name)
        self.channel = Channel(channel_name)
        self._version = ''
        self._sub_version = ''
        self._suffix = ''
        self._text = ''
        self._sdate = '1999-09-09'

        # get all the release info in one shot
        self._conn = sqlite3.connect('relnotes.sqlite')
        for row in self._conn.execute('SELECT version, sub_version, '
                                      ' release_date, release_text '
                                      'FROM Releases '
                                      'WHERE product=? AND channel=? '
                                      'ORDER BY release_date DESC LIMIT 1',
                                      (self.product.idee, self.channel.idee)):
            (self._version, self._sub_version,
             self._sdate, self._text) = row or ("", "", "", "")

        # these are passed in at the command line; they are for release naming
        self._suffix_map = {
            'aurora': options.aurora_suffix,
            'esr': options.esr_suffix,
            'beta': options.beta_suffix
        }

    def cleanup(self, d):
        for key, value in d.items():
            if value is None or value is "":
                del d[key]
            elif isinstance(value, dict):
                self.cleanup(value)
        return d

    @property
    def data(self):
        return {
            'product': self.cleanup(self.product.data),
            'channel': self.cleanup(self.channel.data),
            'path': self.path,
            'filename': self.filename,
            'notes': self.notes_data,
            'text': self.text,
            'version': self.version,
            'sub_version': self.sub_version,
            'date': datetime.strftime(
                self.date, "%B %d, %Y").replace(" 0", " ")
        }

    @property
    def json(self):
        return json.dumps(self.cleanup(self.data), sort_keys=True, indent=2)

    # ex: 20, 21, 22
    @property
    def version(self):
        return self._version

    # ex: 1, 2, 3
    @property
    def sub_version(self):
        return self._sub_version

    # a python date object
    @property
    def date(self):
        return datetime.strptime(self._sdate, "%Y-%m-%d")

    # release text
    @property
    def text(self):
        return self._text

    # ex: 22.0.0a2
    @property
    def version_string(self):
        vs = '%s.0' % self.version
        if (self.sub_version > 0):
            vs += '.%s' % self.sub_version
        vs += self.suffix
        return vs

    # ex: auroranotes, releasenotes
    @property
    def release_string(self):
        # these are fixed values used for path creation
        release_string_map = {
            'aurora': 'auroranotes',
            'beta': 'releasenotes',
            'release': 'releasenotes',
            'esr': 'releasenotes'
        }
        if (self.channel.slug in release_string_map):
            return release_string_map[self.channel.slug]

    # a2, beta
    @property
    def suffix(self):
        if (self.channel.slug in self._suffix_map):
            return self._suffix_map[self.channel.slug]
        return ""

    # /en-US/mobile/20.0.1/releasenotes/
    @property
    def path(self):
        ps = self.product.slug
        if 'esr' in self.product.slug:
            ps = 'firefox'
        return 'en-US/%s/%s/%s/' % (
            ps, self.version_string, self.release_string)

    # index.json
    @property
    def filename(self):
        return 'index.json'

    # an array of whats_new notes
    @property
    def whats_new(self):
        if (not hasattr(self, '_whats_new')):
            self._whats_new = []

            # esr gets a different query, so we have an adapter for that
            adapter = {}
            if 'esr' in self.channel.slug:
                adapter['fixed_in'] = 'fixed_in_subversion'
                adapter['version'] = self.sub_version
            else:
                adapter['fixed_in'] = 'fixed_in_version'
                adapter['version'] = self.version

            q = """SELECT Notes.description, Tags.tag_text FROM Notes
                LEFT OUTER JOIN Tags ON Notes.tag=Tags.id
                WHERE bug_num IS NULL AND
                (product IS NULL OR product=?) AND %s=?
                AND (fixed_in_channel IS NULL OR fixed_in_channel<=?)
                ORDER BY Tags.sort_num ASC, Notes.sort_num DESC
                """ % adapter['fixed_in']

            for row in self._conn.execute(
                    q, (self.product.idee,
                        adapter['version'],
                        self.channel.idee)):
                            self._whats_new.append(
                                Note(
                                    tipe='whats_new',
                                    description=row[0],
                                    tag=row[1]))

        return self._whats_new

    # an array of fixed notes
    @property
    def fixed(self):
        if (not hasattr(self, '_fixed')):
            self._fixed = []
            for row in self._conn.execute(
                'SELECT bug_num,description FROM Notes '
                'WHERE bug_num IS NOT NULL AND '
                '(product IS NULL OR product=?) AND '
                'fixed_in_version=? AND '
                '(fixed_in_channel IS NULL OR fixed_in_channel<=?) '
                'ORDER BY sort_num DESC',
                    (self.product.idee,
                     self.version,
                     self.channel.idee)):
                        self._fixed.append(
                            Note(
                                tipe='fixed',
                                description=row[1],
                                bug=row[0]))
        return self._fixed

    # an array of known_issues notes
    @property
    def known_issues(self):
        if (not hasattr(self, '_known_issues')):
            self._known_issues = []
            for row in self._conn.execute(
                'SELECT Notes.bug_num, Notes.description, '
                ' Notes.fixed_in_version, Channels.channel_name, '
                ' Notes.first_version FROM Notes '
                'LEFT OUTER JOIN Channels '
                'ON Notes.fixed_in_channel=Channels.id '
                'WHERE bug_num IS NOT NULL AND '
                ' (product IS NULL OR product=?) AND '
                ' (first_version<? OR '
                '  (first_version=? AND '
                '    (first_channel IS NULL OR first_channel<=?))) AND '
                ' (fixed_in_version IS NULL OR fixed_in_version>? OR '
                '  (fixed_in_version=? AND fixed_in_channel>?)) '
                'ORDER BY sort_num DESC',
                    (self.product.idee, self.version, self.version,
                     self.channel.idee, self.version, self.version,
                     self.channel.idee)):
                        self._known_issues.append(
                            Note(
                                tipe='known_issues',
                                description=row[1],
                                bug=row[0],
                                fixed_in_version=row[2],
                                fixed_in_channel=row[3],
                                first_version=row[4]))

        return self._known_issues

    # all the notes in one array
    @property
    def notes(self):
        n = []
        n.extend(self.whats_new)
        n.extend(self.fixed)
        n.extend(self.known_issues)
        return n

    # the data of all the notes in one array
    @property
    def notes_data(self):
        d = []
        for n in self.notes:
            d.append(self.cleanup(n.data))
        return d
