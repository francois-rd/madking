from collections import OrderedDict


class TranspositionTable:
    """
    A transposition table to memoize game states explored through game search.
    """

    def __init__(self, max_size, replacement_policy):
        """
        Creates and initializes a new TranspositionTable.

        :param max_size: the maximum number of entries in the table
        :type max_size: integral
        :param replacement_policy: a function that takes a TranspositionTable,
            a key, and a value, and returns another key, which is of one of the
            entries in the table whose value is the best candidate for removal
            when the table is full and a new entry must be added
        :type replacement_policy: (TranspositionTable, X, Y) => X, where X is
            the type of the keys in this table, and Y is the type of the values
        """
        self._table = OrderedDict()
        self._max_size = max_size
        self._current_size = 0
        self._replacement_policy = replacement_policy

    def __setitem__(self, key, value):
        """
        Adds an entry to this TranspositionTable. If the table is full, an
        existing entry is removed from the table before the new entry is added.
        Returns the value of the removed entry or None if no entry was removed.

        :param key: the key of the new table entry
        :param value: the value of the new table entry
        :return: the value of the removed entry or None if no entry was removed
        """
        if self._current_size == self._max_size:
            old = self._table.pop(self._replacement_policy(self, key, value))
        else:
            self._current_size += 1
            old = None
        self._table[key] = value
        return old

    def __getitem__(self, key):
        """
        Returns the value of the entry with the given key.

        :param key: the key of the entry
        :return: the value of the entry
        """
        return self._table[key]

    def __iter__(self):
        """
        Returns a key iterator for this TranspositionTable.

        :return: a key iterator for this TranspositionTable
        :rtype: iterator
        """
        return self._table.__iter__()

    def get(self, key, default=None):
        """
        Returns the value of the entry with the given key, or the given default
        value if this TranspositionTable does not contain an entry with the
        given key.

        :param key: the key of the entry
        :param default: the default to return if there is no entry with the key
        :return: the value of the entry with the given key, or the default
        """
        return self._table.get(key, default)

    def to_json_serializable(self):
        """
        Returns a JSON serializable representation of this TranspositionTable.

        :return: a JSON serializable representation of this TranspositionTable
        """
        return {
            'table': self._table,
            'max-size': self._max_size,
            'current-size': self._current_size,
            'replacement-policy': self._replacement_policy.__name__
        }

    @staticmethod
    def from_json_serializable(json_object):
        table = TranspositionTable(json_object['max-size'], None)
        table._table = OrderedDict(json_object['table'].items())
        table._current_size = json_object['current-size']
        table._replacement_policy = getattr(table,
                                            json_object['replacement-policy'])
        return table

    # ========== REPLACEMENT POLICIES ========== #

    def always_replace(self, key, value):
        """
        Returns the first key in this TranspositionTable.
        :return: the first key in this TranspositionTable
        """
        if self._table.get(key) is not None:  # Replace if something is there.
            return key
        else:  # If no previous entry for that key
            return self._table.__iter__().__next__()  # Replace oldest.
