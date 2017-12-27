import operator

with open(r"Reversi/book.gam", "r") as file:
    games=file.readlines()
    opening_hist = dict()
    for game in games:
        opening = game[:30]
        if opening not in opening_hist:
            opening_hist[opening] = 1
        else:
            opening_hist[opening] += 1
    sorted_hist = sorted(opening_hist.items(), key=operator.itemgetter(1), reverse=True)
    sorted_hist = sorted_hist[:70]

#Writes an opening book of the 70 first entries
with open(r"Reversi/opening_book.gam", "w") as file:
    for entry in sorted_hist:
        file.write(str(entry[0]) + " " + str(entry[1]) + "\n")
