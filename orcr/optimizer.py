import pandas as pd
import numpy as np
from . import optimize_column_rebar
from .utils import get_col_As_section_info

class ColumnRebarOptimizer():
    def __init__(self):
        pass

    def generate_from_excel(self, excel_filename):
        self.excel_filename = excel_filename
        self.column_df = pd.read_excel(excel_filename)
        self.get_columns_info(self.column_df)

    def generate_from_ydb(self, dbs_path):
        self.all_info = get_col_As_section_info(dbs_path)
        self.columns_info = self.all_info[['b', 'h', 'b_As', 'h_As', 'c_As', 'all_As']]
        return(self.columns_info)

    @classmethod
    def calc_column_As(cls, bn, bd, hn, hd, cd):
        cA = np.pi * cd ** 2 / 4
        bA = np.pi * bd ** 2 / 4
        hA = np.pi * hd ** 2 / 4
        b_As = 2 * cA + bn * bA
        h_As = 2 * cA + hn * hA
        c_As = cA
        all_As = 4 * cA + 2 * bn * bA + 2 * hn * hA
        return(b_As, h_As, c_As, all_As)

    def get_columns_info(self, df):
        b_As, h_As, c_As, all_As = self.calc_column_As(df.bn, df.bd, df.hn, df.hd, df.cd)
        columns_data = np.column_stack([df.b, df.h, b_As, h_As, c_As, all_As])
        self.columns_info = pd.DataFrame(columns_data, columns=['b', 'h', 'b_As', 'h_As', 'c_As', 'all_As'])
        self.columns_info[['b', 'h']] = self.columns_info[['b', 'h']].astype(np.int64)
        return(self.columns_info)

    def optimize(self, stirrup_d=8, stirrup_legs_spacing_max=None,
                 pt_min=20, min_As_rate=None, bn_input=None, hn_input=None, hideOutput=True, ignore_pt_constraint=True):
        result = []
        for index, row in self.columns_info.iterrows():
            b, h, b_As, h_As, c_As, all_As = row
            one = optimize_column_rebar(b, h, b_As, h_As, c_As,
                                        stirrup_d=stirrup_d,
                                        stirrup_legs_spacing_max=stirrup_legs_spacing_max,
                                        pt_min=pt_min,
                                        min_As_rate=min_As_rate,
                                        bn_input=bn_input,
                                        hn_input=hn_input,
                                        hideOutput=hideOutput,
                                        ignore_pt_constraint=ignore_pt_constraint)
            if one is None:
                one = [None] * 8
            one = [row.b, row.h] + one
            result.append(one)
        self.optimized_df = pd.DataFrame(result, columns=['b', 'h', 'bn', 'bd', 'hn', 'hd', 'cd', 'pt', 'b_nt', 'h_nt'])
        self.optimized_df[['b', 'h']] = self.optimized_df[['b', 'h']].astype(np.int64)

        df = self.optimized_df
        optimized_rebar = np.column_stack(self.calc_column_As(df.bn, df.bd, df.hn, df.hd, df.cd))
        self.optimized_rebar = pd.DataFrame(optimized_rebar, columns=['b_As', 'h_As', 'c_As', 'all_As'])

        return(self.optimized_df)

    def compare(self):
        # orginal
        columns = ['b_As', 'h_As', 'c_As', 'all_As']
        df = self.column_df
        origial_rebar = np.column_stack(self.calc_column_As(df.bn, df.bd, df.hn, df.hd, df.cd))
        self.origial_rebar = pd.DataFrame(origial_rebar, columns=columns)
        # comparison
        self.comparison = pd.DataFrame(self.optimized_rebar / self.origial_rebar, columns=columns)
        return(self.comparison)

    @property
    def comparison_statistics(self):
        self.compare()
        return(self.comparison.describe())

    def to_excel(self, filename):
        self.optimized_df.to_excel(filename)
