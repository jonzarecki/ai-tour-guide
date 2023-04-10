# Load data from PostgreSQL dump file into a DataFrame
import pickle

with open("wikipedia-2019-11.sql", "r", encoding="UTF-8") as f:
    data = f.read()

splits = data.split("COPY")
query = splits[1]
rows = query.split("\n")

d_coord = dict()
d_wikidata = dict()
d_name = dict()

for r in rows[1:]:
    s = r.split("\t")
    try:
        importance = round(float(s[-5]), 4)
        if importance > 0.01:
            if s[5] != "\\N":
                lat, lon = round(float(s[5]), 4), round(float(s[6]), 4)
                d_coord[(lat, lon)] = max(d_coord.get((lat, lon), -1), importance)
            wikidata = s[-2]
            if wikidata != "\\N":
                d_wikidata[wikidata] = max(d_wikidata.get(wikidata, -1), importance)
            name = s[1].lower().replace("-", "").replace("_", "").replace("'", "").replace(" ", "")
            if name != "\\N":
                d_name[name] = max(d_name.get(name, -1), importance)
    except:
        print(r)
        continue

with open("importance_dict_coord.pkl", "wb") as f:
    pickle.dump(d_coord, f)

with open("importance_dict_wikidata.pkl", "wb") as f:
    pickle.dump(d_wikidata, f)

with open("importance_dict_name.pkl", "wb") as f:
    pickle.dump(d_name, f)
