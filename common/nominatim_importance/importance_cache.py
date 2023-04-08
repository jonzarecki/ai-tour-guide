import os
import pickle

_curdir = os.path.dirname(__file__)


class ImportanceCache:
    def __init__(self):
        with open(f"{_curdir}/importance_dict_coord.pkl", 'rb') as f:
            self.importance_dict_coord = pickle.load(f)

        with open(f"{_curdir}/importance_dict_wikidata.pkl", 'rb') as f:
            self.importance_dict_wikidata = pickle.load(f)

        with open(f"{_curdir}/importance_dict_name.pkl", 'rb') as f:
            self.importance_dict_name = pickle.load(f)
            self.names_set = set(self.importance_dict_name.keys())

    def __getitem__(self, n):
        lat, lon = round(float(n.lat), 4), round(float(n.lon), 4)
        wikidata = n.tags.get('wikidata', None)
        name = n.tags.get('name', None)
        if name is not None:
            name = name.lower().replace('-', '').replace('_', '').replace('\'', '').replace(' ', '')
        cached_importance = max(self.importance_dict_coord.get((lat, lon), -1),
                                self.importance_dict_wikidata.get(wikidata, -1))
        if cached_importance != -1:
            return cached_importance


        if name is not None:
            for n in self.names_set:
                if name in n:
                    return self.importance_dict_name[n]

        return -1


importance_cache = ImportanceCache()
