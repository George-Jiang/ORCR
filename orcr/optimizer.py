import pandas as pd
import numpy as np
from . import optimize_column_rebar


class ColumnRebarOptimizer():
    def __init__(self):
        pass

    def generate_from_excel(self, excel_filename):
        self.excel_filename = excel_filename
        self.column_df = pd.read_excel(excel_filename)
        self.get_columns_info(self.column_df)

    @classmethod
    def calc_column_As(cls, bn, bd, hn, hd, cd):
        cA = np.pi * cd ** 2 / 4 / 100
        bA = np.pi * bd ** 2 / 4 / 100
        hA = np.pi * hd ** 2 / 4 / 100
        b_As = 2 * cA + bn * bA
        h_As = 2 * cA + hn * hA
        c_As = cA
        all_As = 4 * cA + 2 * bn * bA + 2 * hn * hA
        return(b_As, h_As, c_As, all_As)

    def get_columns_info(self, df):
        b_As, h_As, c_As, all_As = self.calc_column_As(df.bn, df.bd, df.hn, df.hd, df.cd)
        columns_data = np.column_stack([df.b, df.h, b_As, h_As, c_As, all_As])
        self.columns_info = pd.DataFrame(columns_data, columns=['b', 'h', 'b_As', 'h_As', 'c_As', 'all_As'])
        return(self.columns_info)

    def optimize(self, stirrup_d=8, pt_min=20, bn_input=None, hn_input=None):
        result = []
        for index, row in self.columns_info.iterrows():
            one = optimize_column_rebar(*row[:-1],
                                        stirrup_d=stirrup_d, pt_min=pt_min,
                                        bn_input=bn_input, hn_input=hn_input)
            if one == None:
                one = [None] * 8
            one = [row.b, row.h] + one
            result.append(one)
        self.optimized_df = pd.DataFrame(result, columns=['b', 'h', 'bn', 'bd', 'hn', 'hd', 'cd', 'pt', 'b_nt', 'h_nt'])
        return(self.optimized_df)

    def compare(self):
        # orginal
        columns = ['b_As', 'h_As', 'c_As', 'all_As']
        df = self.column_df
        origial_rebar = np.column_stack(self.calc_column_As(df.bn, df.bd, df.hn, df.hd, df.cd))
        self.origial_rebar = pd.DataFrame(origial_rebar, columns=columns)
        # optimized
        df = self.optimized_df
        optimized_rebar = np.column_stack(self.calc_column_As(df.bn, df.bd, df.hn, df.hd, df.cd))
        self.optimized_rebar = pd.DataFrame(optimized_rebar, columns=columns)
        # comparison
        self.comparison = pd.DataFrame(self.optimized_rebar / self.origial_rebar, columns=columns)
        return(self.comparison)

    @property
    def comparison_statistics(self):
        self.compare()
        return(self.comparison.describe())

    def to_excel(self, filename):
        self.optimized_df.to_excel(filename)
