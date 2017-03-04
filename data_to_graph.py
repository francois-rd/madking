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



fig = plt.figure()
plt.xlabel('move number')
plt.ylabel('Time in seconds')

plt.title('Alpha beta depth 4, simple_eval, king time vs dragon time')
y_king = ([ x['time'] for x in data if (x["search"] == "alpha_beta" and
         x["evaluate"] == "simple_eval" and int(x["max_depth"]) == 4 and
         int(x["table_max_size"]) == 1000000 and x["player"] == "king")])

y_dragon = ([ x['time'] for x in data if (x["search"] == "alpha_beta" and
         x["evaluate"] == "simple_eval" and int(x["max_depth"]) == 4 and
         int(x["table_max_size"]) == 1000000 and x["player"] == "dragon")])

x = [i for i in range(len(y_king))]

line1,  = plt.plot(x,y_king, '-', label="King")
line2, = plt.plot(x,y_dragon, '--', label="Dragon")
first_legend = plt.legend(handles=[line1, line2], loc=1)
ax = plt.gca().add_artist(first_legend)
plt.show()





