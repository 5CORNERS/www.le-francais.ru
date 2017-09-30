import pandas as pd

def import_from_excel(fp):
    df = pd.read_excel(fp, 0)
    dict = df.to_dict()
    return dict


