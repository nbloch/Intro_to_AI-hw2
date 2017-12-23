import operator

with open(r"D:\OneDrive\Documents\Etudes\Technion\236501 - Introduction to AI\תרגילי בית\HW2\hw2\book.gam", "r") as file:
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
    print(sorted_hist)