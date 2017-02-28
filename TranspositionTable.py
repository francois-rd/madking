from collections import OrderedDict

"""
Each table entry corresponds to one state of the game (in this context, a
'state' is a board position as well as which player's turn it is).

The table keys will be the hash strings returned by state.hash_state().
The table values will be tuples of the form:
    (<depth>, <score>, <move>, <exact-alpha-or-beta>)
where
    <depth> is the depth in number of edges of the explored subtree rooted at
        the corresponding state
    <score> is the utility value of the corresponding state
    <move> is the move that leads to the best possible child state (i.e. the
        move that will lead to the value of <score> being correct)
    <exact-alpha-or-beta> (used for minimax search with alpha beta pruning) is
        a byte that equals the constant
            EXACT iff <score> is an exact value
            ALPHA_CUTOFF iff <score> is an alpha cutoff
            BETA_CUTOFF iff <score> is a beta cutoff
"""

DEPTH_INDEX = 0
SCORE_INDEX = 1
MOVE_INDEX = 2
FLAGS_INDEX = 3

EXACT = 0b00000000
ALPHA_CUTOFF = 0b00000001
BETA_CUTOFF = 0b00000010


class TranspositionTable:
    """
    A transposition table to memoize game states explored through game search.
    The table's entries are ordered by order of insertion, so the first entry
    is the one that was inserted longest ago, while the last entry is the one
    that was inserted most recently.
    """

    def __init__(self, max_size, replacement_policy):
        """
        Creates and initializes a new TranspositionTable.

        :param max_size: the maximum number of entries in the table
        :type max_size: integral
        :param replacement_policy: a function that takes a TranspositionTable,
            a key, and a value, and adds the key-value pair to the table if it
            is not full, or else determines the best candidate for removal and
            replaces that entry with the new key-value pair. The best candidate
            might be the given key-value pair, in which case it is not added
            (i.e. the new entry is rejected)
        :type replacement_policy: (TranspositionTable, X, Y) => None, where X
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
        self._number_entries_swapped = 0
        self._number_directly_added = 0
        self._number_safe_accesses = 0
        self._number_hits = 0
        self._replacement_policy = replacement_policy

    def __setitem__(self, key, value):
        """
        Adds an entry to this TranspositionTable using the replacement policy.
        If the table is full, the replacement policy is also used to find an
        existing entry to replace. The policy may also determined that no entry
        should be replaced, in which case the new entry is simply rejected
        (i.e. not added to the table).

        :param key: the key of the new table entry
        :param value: the value of the new table entry
        """
        self._replacement_policy(self, key, value)

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

    def __len__(self):
        """
        Returns the number of entries in this TranspositionTable.

        :return: the number of entries in this TranspositionTable
        :rtype: integral
        """
        return self._current_size

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

    def reset_counters(self):
        """
        Resets the following counters to 0, without also clearing the table:
            number_attempted_mutations
            number_entries_replaced
            number_entries_rejected
            number_direct_accesses
            number_entries_swapped
            number_directly_added
            number_safe_accesses
            number_hits
        """
        self._number_attempted_mutations = 0
        self._number_entries_replaced = 0
        self._number_entries_rejected = 0
        self._number_direct_accesses = 0
        self._number_entries_swapped = 0
        self._number_directly_added = 0
        self._number_safe_accesses = 0
        self._number_hits = 0

    def get_counters(self):
        """
        Returns a tuple containing the current value of all the counters. The
        counters are ordered as follows:
            number_attempted_mutations
            number_entries_replaced
            number_entries_rejected
            number_direct_accesses
            number_entries_swapped
            number_directly_added
            number_safe_accesses
            number_hits
        """
        return (self._number_attempted_mutations,
                self._number_entries_replaced, self._number_entries_rejected,
                self._number_direct_accesses, self._number_entries_swapped,
                self._number_directly_added, self._number_safe_accesses,
                self._number_hits)

    def get_max_size(self):
        """
        Returns the maximum size of this TranspositionTable.

        :return: the maximum size of this TranspositionTable
        """
        return self._max_size

    def get_replacement_policy(self):
        """
        Returns the replacement policy of this TranspositionTable.

        :return: the replacement policy of this TranspositionTable
        """
        return self._replacement_policy

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
            'number-entries-swapped': self._number_entries_swapped,
            'number-directly-added': self._number_directly_added,
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
        table._number_entries_replaced = json_object['number-entries-replaced']
        table._number_entries_rejected = json_object['number-entries-rejected']
        table._number_direct_accesses = json_object['number-direct-accesses']
        table._number_entries_swapped = json_object['number-entries-swapped']
        table._number_directly_added = json_object['number-directly-added']
        table._number_safe_accesses = json_object['number-safe-accesses']
        table._number_hits = json_object['number-hits']
        table._replacement_policy = getattr(table,
                                            json_object['replacement-policy'])
        return table

    # ========== REPLACEMENT POLICIES ========== #

    def replace_overall_oldest(self, key, value):
        """
        Adds the given key-value pair to the given TranspositionTable, first
        removing the overall oldest entry in the table if the table is already
        full.

        :param key: the key of the new table entry
        :param value: the value of the new table entry
        """
        self._number_attempted_mutations += 1
        if self._current_size == self._max_size:
            self._number_entries_replaced += 1
            del self._table[next(self._table.keys().__iter__())]
        else:
            self._current_size += 1
            self._number_directly_added += 1
        self._table[key] = value

    def replace_older_value_or_else_overall_oldest(self, key, value):
        """
        Adds the given key-value pair to the given TranspositionTable. If an
        entry with the same key is already present in the table, that entry is
        removed and replaced by ("swapped with") the new entry. If the table is
        already full, and no entry with the same key is already present in the
        table, then the given key-value pair replaces the overall oldest entry
        in the table, where "oldest" means "the entry that was last added or
        last replaced longest ago".

        :param key: the key of the new table entry
        :param value: the value of the new table entry
        """
        self._number_attempted_mutations += 1
        if self._table.pop(key, default=None) is None:
            if self._current_size == self._max_size:
                self._number_entries_replaced += 1
                del self._table[next(self._table.keys().__iter__())]
            else:
                self._current_size += 1
                self._number_directly_added += 1
        else:
            self._number_entries_swapped += 1
        self._table[key] = value

    def replace_older_value_or_else_new_entry(self, key, value):
        """
        Conditionally adds the given key-value pair to the given
        TranspositionTable. If an entry with the same key is already present in
        the table, that entry is removed and replaced by ("swapped with") the
        new entry. If the table is not full, and no entry with the same key is
        already present in the table, then the given key-value pair is added to
        the table. If the table is already full, and no entry with the same key
        is already present in the table, then the given key-value pair is
        rejected.

        :param key: the key of the new table entry
        :param value: the value of the new table entry
        """
        self._number_attempted_mutations += 1
        if self._table.pop(key, default=None) is None:
            if self._current_size == self._max_size:
                self._number_entries_rejected += 1
            else:
                self._current_size += 1
                self._number_directly_added += 1
                self._table[key] = value
        else:
            self._number_entries_swapped += 1
            self._table[key] = value

    def replace_shallower_value_or_else_shallower_with_first(self, key, value):
        """
        Conditionally adds the given key-value pair to the given
        TranspositionTable. If the table already contains an entry for the
        given key, then the given key-value pair replaces ("is swapped with")
        the old entry iff the new entry is at least as deep as the old entry
        (otherwise, the new entry is rejected). If the table is not full, and
        no entry with the same key is already present in the table, then the
        given key-value pair is added to the table. If the table is already
        full, and no entry with the same key is already present in the table,
        then the given key-value pair replaces the first entry in the table iff
        the new entry is at least as deep as the first entry (otherwise, the
        new entry is rejected).

        :param key: the key of the new table entry
        :param value: the value of the new table entry
        """
        self._number_attempted_mutations += 1
        value_already_in_table = self._table.pop(key, default=None)
        if value_already_in_table is None:
            if self._current_size == self._max_size:
                first_key = next(self._table.keys().__iter__())
                first_value = self._table.pop(first_key)
                if value[DEPTH_INDEX] >= first_value[DEPTH_INDEX]:
                    self._number_entries_replaced += 1
                else:
                    self._number_entries_rejected += 1
                    key = first_key
                    value = first_value
            else:
                self._current_size += 1
                self._number_directly_added += 1
        else:
            if value[DEPTH_INDEX] >= value_already_in_table[DEPTH_INDEX]:
                self._number_entries_swapped += 1
            else:
                self._number_entries_rejected += 1
                value = value_already_in_table
        self._table[key] = value

    def replace_shallower_value_or_else_overall_oldest(self, key, value):
        """
        Conditionally adds the given key-value pair to the given
        TranspositionTable. If the table already contains an entry for the
        given key, then the given key-value pair replaces ("is swapped with")
        the old entry iff the new entry is at least as deep as the old entry
        (otherwise, the new entry is rejected). If the table is not full, and
        no entry with the same key is already present in the table, then the
        given key-value pair is added to the table. If the table is already
        full, and no entry with the same key is already present in the table,
        then the given key-value pair replaces the overall oldest entry in the
        table, where "oldest" means "the entry that was last added or last
        replaced (including attempted replacements) longest ago".

        :param key: the key of the new table entry
        :param value: the value of the new table entry
        """
        self._number_attempted_mutations += 1
        value_already_in_table = self._table.pop(key, default=None)
        if value_already_in_table is None:
            if self._current_size == self._max_size:
                self._number_entries_replaced += 1
                del self._table[next(self._table.keys().__iter__())]
            else:
                self._current_size += 1
                self._number_directly_added += 1
        else:
            if value[DEPTH_INDEX] >= value_already_in_table[DEPTH_INDEX]:
                self._number_entries_swapped += 1
            else:
                self._number_entries_rejected += 1
                value = value_already_in_table
        self._table[key] = value

    def replace_shallower_value_or_else_new_entry(self, key, value):
        """
        Conditionally adds the given key-value pair to the given
        TranspositionTable. If the table already contains an entry for the
        given key, then the given key-value pair replaces ("is swapped with")
        the old entry iff the new entry is at least as deep as the old entry
        (otherwise, the new entry is rejected). If the table is not full, and
        no entry with the same key is already present in the table, then the
        given key-value pair is added to the table. If the table is already
        full, and no entry with the same key is already present in the table,
        then the given key-value pair is rejected.

        :param key: the key of the new table entry
        :param value: the value of the new table entry
        """
        self._number_attempted_mutations += 1
        value_already_in_table = self._table.pop(key, default=None)
        if value_already_in_table is None:
            if self._current_size == self._max_size:
                self._number_entries_rejected += 1
            else:
                self._current_size += 1
                self._number_directly_added += 1
                self._table[key] = value
        else:
            if value[DEPTH_INDEX] >= value_already_in_table[DEPTH_INDEX]:
                self._number_entries_swapped += 1
                self._table[key] = value
            else:
                self._number_entries_rejected += 1
                self._table[key] = value_already_in_table
