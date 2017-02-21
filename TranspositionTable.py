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
    <exact-alpha-or-beta> is a byte, where
        the first lowest-order bit is set iff <score> is an exact value (as
            opposed to an alpha or beta cutoff)
        the second lowest-order bit is set iff <score> is an alpha cutoff (for
            alpha beta minimax search)
        the third lowest-order bit is set iff <score> is a beta cutoff (for
            alpha beta minimax search)
"""

DEPTH_INDEX = 0
SCORE_INDEX = 1
MOVE_INDEX = 2
EXACT_ALPHA_BETA_INDEX = 3

_EXACT_MASK = 0b00000001
_ALPHA_MASK = 0b00000010
_BETA_MASK = 0b00000100


def set_flags(exact=False, alpha_cutoff=False, beta_cutoff=False):
    """
    A convenience function that does the equivalent of applying each of
    'set_exact', 'set_alpha_cutoff', and 'set_beta_cutoff' in turn (but much
    more efficiently!!!) and then returning the overall result. This function
    should be called over the individual ones whenever possible.

    :param exact: the new value for the "exact" bit
    :type exact: bool
    :param alpha_cutoff: the new value for the "alpha cutoff" bit
    :type alpha_cutoff: bool
    :param beta_cutoff: the new value for the "beta cutoff" bit
    :type beta_cutoff: bool
    :return: a copy of 'exact_alpha_or_beta' with each of the "exact", "alpha
        cutoff", and "beta cutoff" bits potentially modified
    :rtype: byte
    """
    return (((beta_cutoff << 1) | alpha_cutoff) << 1) | exact


def is_exact(exact_alpha_or_beta):
    """
    Returns True iff the "exact" bit of 'exact_alpha_or_beta' is set.

    :param exact_alpha_or_beta: the <exact-alpha-or-beta> field of a
        TranspositionTable value
    :type exact_alpha_or_beta: byte
    :return: True iff the "exact" bit of 'exact_alpha_or_beta' is set
    :rtype: bool
    """
    return bool(exact_alpha_or_beta & _EXACT_MASK)


def set_exact(exact_alpha_or_beta, exact):
    """
    Returns a copy of 'exact_alpha_or_beta', modified so that the "exact" bit
    is set if 'exact' is True, and cleared if 'exact' is False.

    :param exact_alpha_or_beta: the <exact-alpha-or-beta> field of a
        TranspositionTable value
    :type exact_alpha_or_beta: byte
    :param exact: the new value for the "exact" bit
    :type exact: bool
    :return: a copy of 'exact_alpha_or_beta' with the "exact" bit potentially
        modified
    :rtype: byte
    """
    return ((exact_alpha_or_beta >> 1) << 1) | exact


def is_alpha_cutoff(exact_alpha_or_beta):
    """
    Returns True iff the "alpha cutoff" bit of 'exact_alpha_or_beta' is set.

    :param exact_alpha_or_beta: the <exact-alpha-or-beta> field of a
        TranspositionTable value
    :type exact_alpha_or_beta: byte
    :return: True iff the "alpha cutoff" bit of 'exact_alpha_or_beta' is set
    :rtype: bool
    """
    return bool(exact_alpha_or_beta & _ALPHA_MASK)


def set_alpha_cutoff(exact_alpha_or_beta, alpha_cutoff):
    """
    Returns a copy of 'exact_alpha_or_beta', modified so that the "alpha
    cutoff" bit is set if 'alpha_cutoff' is True, and cleared if 'alpha_cutoff'
    is False.

    :param exact_alpha_or_beta: the <exact-alpha-or-beta> field of a
        TranspositionTable value
    :type exact_alpha_or_beta: byte
    :param alpha_cutoff: the new value for the "alpha cutoff" bit
    :type alpha_cutoff: bool
    :return: a copy of 'exact_alpha_or_beta' with the "alpha cutoff" bit
        potentially modified
    :rtype: byte
    """
    return exact_alpha_or_beta ^ ((-alpha_cutoff ^ int(exact_alpha_or_beta))
                                  & _ALPHA_MASK)


def is_beta_cutoff(exact_alpha_or_beta):
    """
    Returns True iff the "beta cutoff" bit of 'exact_alpha_or_beta' is set.

    :param exact_alpha_or_beta: the <exact-alpha-or-beta> field of a
        TranspositionTable value
    :type exact_alpha_or_beta: byte
    :return: True iff the "beta cutoff" bit of 'exact_alpha_or_beta' is set
    :rtype: bool
    """
    return bool(exact_alpha_or_beta & _BETA_MASK)


def set_beta_cutoff(exact_alpha_or_beta, beta_cutoff):
    """
    Returns a copy of 'exact_alpha_or_beta', modified so that the "beta cutoff"
    bit is set if 'beta_cutoff' is True, and cleared if 'beta_cutoff' is False.

    :param exact_alpha_or_beta: the <exact-alpha-or-beta> field of a
        TranspositionTable value
    :type exact_alpha_or_beta: byte
    :param beta_cutoff: the new value for the "beta cutoff" bit
    :type beta_cutoff: bool
    :return: a copy of 'exact_alpha_or_beta' with the "beta cutoff" bit
        potentially modified
    :rtype: byte
    """
    return exact_alpha_or_beta ^ ((-beta_cutoff ^ int(exact_alpha_or_beta))
                                  & _BETA_MASK)


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

        :param key: the key of the new table entry
        :param value: the value of the new table entry
        """
        self._number_attempted_mutations += 1
        if self._current_size == self._max_size:
            key_to_remove, value_to_remove = \
                self._replacement_policy(self, key, value)
            if key_to_remove == key and value_to_remove == value:
                self._number_entries_rejected += 1
            else:
                self._number_entries_replaced += 1
                del self._table[key_to_remove]
                self._table[key] = value
        else:
            self._current_size += 1
            self._table[key] = value

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

    def replace_overall_oldest(self, key, value):
        """
        Returns the first/oldest (<key>, <value>) pair in the given
        TranspositionTable.

        :param key: the key of the new table entry
        :param value: the value of the new table entry
        :return: the first/oldest entry in the given TranspositionTable
        """
        return next(self._table.items())

    def replace_older_value_or_else_overall_oldest(self, key, value):
        """
        If the table already contains an entry for the given key, then the
        (<key>, <value>) pair of that entry is returned. Otherwise, the first/
        oldest (<key>, <value>) pair in the given TranspositionTable is
        returned.

        :param key: the key of the new table entry
        :param value: the value of the new table entry
        :return: the table entry for the given key, or the first/oldest entry
            in the TranspositionTable if no such entry exists
        """
        value_already_in_table = self._table.get(key)
        if value_already_in_table is not None:
            return key, value_already_in_table
        return next(self._table.items())

    def replace_older_value_or_else_new_entry(self, key, value):
        """
        If the table already contains an entry for the given key, then the
        (<key>, <value>) pair of that entry is returned. Otherwise, the new
        entry is returned.

        :param key: the key of the new table entry
        :param value: the value of the new table entry
        :return: the table entry for the given key, or the new entry if no such
            entry exists
        """
        value_already_in_table = self._table.get(key)
        if value_already_in_table is not None:
            return key, value_already_in_table
        return key, value

    def replace_shallower_value_or_else_some_shallower(self, key, value):
        """
        If the table already contains an entry for the given key, then the
        (<key>, <value>) pair of that entry is returned iff the depth of the
        new entry is greater than the depth of the existing entry. Otherwise,
        the first (<key>, <value>) pair in the given TranspositionTable that
        has depth less than that of the new entry is returned (the new entry is
        returned iff it is shallower than every other entry in the table).

        :param key: the key of the new table entry
        :param value: the value of the new table entry
        :return: the table entry for the given key if it is shallower than the
            new entry, or the first entry in the TranspositionTable that is
            shallower than the new entry, or else the new entry itself if no
            such entry exists
        """
        depth = value[DEPTH_INDEX]
        value_already_in_table = self._table.get(key)
        if value_already_in_table is not None:
            if depth > value_already_in_table[DEPTH_INDEX]:
                return key, value_already_in_table
        for k, v in self._table.items():
            if depth > v[DEPTH_INDEX]:
                return k, v
        return key, value

    def replace_shallower_value_or_else_overall_oldest(self, key, value):
        """
        If the table already contains an entry for the given key, then the
        (<key>, <value>) pair of that entry is returned iff the depth of the
        new entry is greater than the depth of the existing entry. Otherwise,
        the first/oldest (<key>, <value>) pair in the given TranspositionTable
        is returned.

        :param key: the key of the new table entry
        :param value: the value of the new table entry
        :return: the table entry for the given key if it is shallower than the
            new entry, or the first/oldest entry in the TranspositionTable if
            no such entry exists or it is not shallower
        """
        value_already_in_table = self._table.get(key)
        if value_already_in_table is not None:
            if value[DEPTH_INDEX] > value_already_in_table[DEPTH_INDEX]:
                return key, value_already_in_table
        return next(self._table.items())

    def replace_shallower_value_or_else_new_entry(self, key, value):
        """
        If the table already contains an entry for the given key, then the
        (<key>, <value>) pair of that entry is returned iff the depth of the
        new entry is greater than the depth of the existing entry. Otherwise,
        the new entry is returned.

        :param key: the key of the new table entry
        :param value: the value of the new table entry
        :return: the table entry for the given key if it is shallower than the
            new entry, or the new entry if no such entry exists or it is not
            shallower
        """
        value_already_in_table = self._table.get(key)
        if value_already_in_table is not None:
            if value[DEPTH_INDEX] > value_already_in_table[DEPTH_INDEX]:
                return key, value_already_in_table
        return key, value

    def replace_smaller_subtree_or_else_some_smaller(self, key, value):
        """
        If the table already contains an entry for the given key, then the
        (<key>, <value>) pair of that entry is returned iff the size of the
        subtree rooted at the new entry is greater than the size of the subtree
        rooted at the existing entry. Otherwise, the first (<key>, <value>)
        pair in the given TranspositionTable whose size is less than that of
        the new entry is returned (so the new entry is returned iff it is
        smaller than every other entry in the table).

        :param key: the key of the new table entry
        :param value: the value of the new table entry
        :return: the table entry for the given key if the subtree rooted at it
            is smaller than that of the new entry, or the first entry in the
            TranspositionTable whose size is less than that of the new entry,
            or else the new entry itself if no such entry exists
        """
        pass

    def replace_smaller_subtree_or_else_overall_oldest(self, key, value):
        """
        If the table already contains an entry for the given key, then the
        (<key>, <value>) pair of that entry is returned iff the size of the
        subtree rooted at the new entry is greater than the size of the subtree
        rooted at the existing entry. Otherwise, the first/oldest
        (<key>, <value>) pair in the given TranspositionTable is returned.

        :param key: the key of the new table entry
        :param value: the value of the new table entry
        :return: the table entry for the given key if the subtree rooted at it
            is smaller than that of the new entry, or the first/oldest entry in
            the TranspositionTable if no such entry exists or it is not smaller
        """
        pass

    def replace_smaller_subtree_or_else_new_entry(self, key, value):
        """
        If the table already contains an entry for the given key, then the
        (<key>, <value>) pair of that entry is returned iff the size of the
        subtree rooted at the new entry is greater than the size of the subtree
        rooted at the existing entry. Otherwise, the new entry is returned.

        :param key: the key of the new table entry
        :param value: the value of the new table entry
        :return: the table entry for the given key if the subtree rooted at it
            is smaller than that of the new entry, or the new entry if no such
            entry exists or it is not smaller
        """
        pass

    def replace_two_deep(self, key, value):
        """
        From: Breucker, D., et al. (1998).
        """
        # TODO: is this even worth implementing?
        pass

    def replace_two_big(self, key, value):
        """
        From: Breucker, D., et al. (1998).
        """
        # TODO: is this even worth implementing?
        pass
