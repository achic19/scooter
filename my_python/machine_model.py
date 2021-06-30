import pandas as pd
import numpy as np
from scipy import stats


class MachineModel:
    def __init__(self, bt_scooter):
        self.bt_scooter = bt_scooter[(bt_scooter['OPENTS'] > -1) & (bt_scooter['TOLASTDISCOTS'] > -1)]
        features = bt_scooter[['PK_UID', 'LASTDISCOTS', 'STDCALC', 'AVGCALC', 'TRIPTIME', 'via_to', 'via_to_uni']]
        self.features = features.assign(TRIPTIME2=bt_scooter['CLOSETS'] - bt_scooter['LASTDISCOTS'])
