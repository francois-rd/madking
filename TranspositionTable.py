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
            a key, and a value, and returns a key and a value, which is either
            one of the entries in the table whose value is the best candidate
            for removal when the table is full and a new entry must be added,
            or is the key and value of the given/new entry, which is itself not
            good enough to be added to the table (i.e. the new entry is
            rejected)
        :type replacement_policy: (TranspositionTable, X, Y) => X, Y, where X
            is the type of the keys in this table, and Y is the type of the
            values
        """
        self._table = OrderedDict()
        self._max_size = max_size
        self._current_size = 0
        self._number_attempted_mutations = 0
        self._number_entries_replaced = 0
        self._number_entries_rejected = 0
        self._number_direct_accesses = 0
        self._number_safe_accesses = 0
        self._number_hits = 0
        self._replacement_policy = replacement_policy

    def __setitem__(self, key, value):
        """
        Adds an entry to this TranspositionTable. If the table is full, the
        replacement policy is used to find an existing entry to replace. The
        policy may also determined that no entry should be replaced, in which
        case the new entry is simply rejected (i.e. not added to the table).
        Returns the value of the removed entry, or the given value it was
        rejected, or None if no the table was not already full.

        :param key: the key of the new table entry
        :param value: the value of the new table entry
        :return: the value of the removed entry, or the given value it was
            rejected, or None if no the table was not already full
        """
        self._number_attempted_mutations += 1
        if self._current_size == self._max_size:
            key_to_remove, value_to_remove = \
                self._replacement_policy(self, key, value)
            if key_to_remove == key and value_to_remove == value:
                self._number_entries_rejected += 1
                return value  # Return the new value.
            self._number_entries_replaced += 1
            removed_value = self._table.pop(key_to_remove)
        else:
            self._current_size += 1
            removed_value = None
        self._table[key] = value
        return removed_value

    def __getitem__(self, key):
        """
        Returns the value of the entry with the given key.

        :param key: the key of the entry
        :return: the value of the entry
        """
        self._number_direct_accesses += 1
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
        self._number_safe_accesses += 1
        value = self._table.get(key, default)
        if value is not default:
            self._number_hits += 1
        return value

    def to_json_serializable(self):
        """
        Returns a JSON serializable representation of this TranspositionTable.

        :return: a JSON serializable representation of this TranspositionTable
        """
        return {
            'table': self._table,
            'max-size': self._max_size,
            'current-size': self._current_size,
            'number-attempted-mutations': self._number_attempted_mutations,
            'number-entries-replaced': self._number_entries_replaced,
            'number-entries-rejected': self._number_entries_rejected,
            'number-direct-accesses': self._number_direct_accesses,
            'number-safe-accesses': self._number_safe_accesses,
            'number-hits': self._number_hits,
            'replacement-policy': self._replacement_policy.__name__
        }

    @staticmethod
    def from_json_serializable(json_object):
        """
        Returns a TranspositionTable, given a JSON serializable representation
        of some TranspositionTable. Assumes the replacement policy is an
        instance method defined in the TranspositionTable class.

        :param json_object: a JSON serializable representation of some
            TranspositionTable
        :return: the corresponding TranspositionTable
        :rtype: TranspositionTable
        """
        table = TranspositionTable(json_object['max-size'], None)
        table._table = OrderedDict(json_object['table'].items())
        table._current_size = json_object['current-size']
        table._number_attempted_mutations = \
            json_object['number-attempted-mutations']
        table._number_direct_accesses = json_object['number-direct-accesses']
        table._number_safe_accesses = json_object['number-safe-accesses']
        table._number_hits = json_object['number-hits']
        table._number_entries_replaced = json_object['number-entries-replaced']
        table._number_entries_rejected = json_object['number-entries-rejected']
        table._replacement_policy = getattr(table,
                                            json_object['replacement-policy'])
        return table

    # ========== REPLACEMENT POLICIES ========== #

    def always_replace(self, key, value):
        """
        Returns the first (<key>, <value>) pair in this TranspositionTable.

        :return: the first (<key>, <value>) pair in this TranspositionTable
        """
        return next(self._table.items())  # Replace oldest.
