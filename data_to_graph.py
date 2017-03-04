file = open("data.csv")
keys_list = ["search","evaluate","max_depth","move_number","player","time",
             "replacement_policy","table_max_size","table_current_size",
             "table_number_attempted_mutations","table_number_entries_replaced",
             "table_number_entries_rejected","table_number_direct_accesses",
             "table_number_entries_swapped","table_number_directly_added",
             "table_number_safe_accesses","table_number_hits","num_term","num_leafs",
             "num_usable_hits","num_usable_hits_exact","num_usable_hits_alpha",
             "num_usable_hits_beta","num_usable_hits_pruning",
             "num_move_ordering_alpha_cutoff",
             "num_move_ordering_beta_cutoff","num_alpha_cutoff","num_beta_cutoff"]
import matplotlib.pyplot as plt


def _cond_check(condition, data_value):
    for i in condition:
        if i != "label" and condition[i] != data_value[i]:
            return False
    return True


def _get_data_dict_from_cond(condition,  data):
    return [x for x in data if _cond_check(condition, x)]


def _get_data_list_from_cond(condition, plot_of, data):
    return [x[plot_of] for x in data if _cond_check(condition, x)]


def plot_conditions(conditions, plot_of, data, title, x_axix, y_axis):
    """
    Plots the graph,
    data is a list of dictionary like
     [{"A":1, "B":"minimax","C":100 }, {"A":2,"B":"minimax","C":100},
     {"A":3,"B":"alpha-beta","C":100} ]
     plot_of would "A"
     conditions:
     [{"B":"mini-max", "label":"MINIMAX"}, {"C":200, "label": "C is 200"}]
     Now plot with 2 lines, satisfying conditions, will be plotted.

    :param conditions: list of expects all the conditions on dictionary for keys in data.
            every condition should also have a label, to label that line.
    :param plot_of: what variable do you wanna plot, key of that
    :param data: list of dictionaries, with data
    :param title: What should be the title
    :param x_axis: What should be the x-axis
    :param y_axis: What should be the y-axis
    :return:Nothing
    """

    plt.xlabel(x_axix)
    plt.ylabel(y_axis)
    plt.title(title)

    lines = []
    for cond in conditions:
        lines.append( _get_data_list_from_cond(cond, plot_of, data))

    x = [i for i in range(len(lines[0]))]

    lines_plot = []
    for i in range(len(lines)):
        l, = plt.plot(x, lines[i], '-', label=conditions[i]["label"])
        lines_plot.append(l)

    first_legend = plt.legend(handles=lines_plot, loc=1)
    plt.gca().add_artist(first_legend)
    plt.show()




c1 = {

    "search": "alpha_beta",
    "evaluate": "simple_eval",
    "max_depth": "4",
    "table_max_size":"1000000",
    "player":"dragon",
    "label":"dragon"
}
c2 = {

    "search": "alpha_beta",
    "evaluate": "simple_eval",
    "max_depth": "4",
    "table_max_size":"1000000",
    "player":"king",
    "label":"king"
}

data = []
for f in file:
    d = {}
    if f.isspace():
        break
    line = f.rstrip().split(",")
    i = 0
    for key in keys_list:
        d[key] = line[i]
        i += 1
    data.append(d)


plot_conditions([c1, c2], "time", data, title = "Alpha beta depth 4, simple_eval"
                                                ", king time vs dragon time",
                x_axix = "Move Number", y_axis = "Time in seconds")