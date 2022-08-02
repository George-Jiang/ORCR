import sqlite3
import pandas as pd
import numpy as np

def get_setion(dbname):
    section_sql = '''
                    SELECT columns.ID, columnsect.ShapeVal, joint.X, joint.Y, 
                    columns.Rotation, PC.ID as if_pre ,floor.Height, floor.No_ as floor
                    FROM
                    tblColSeg as columns
                    INNER JOIN
                    tblJoint as joint
                    on columns.JtID = joint.ID
                    INNER JOIN
                    tblColSect as columnsect
                    on columns.SectID = columnsect.ID
                    LEFT JOIN
                    tblPC as PC
                    on columns.ID = PC.ElementId
                    INNER JOIN
                    tblFloor as floor
                    on columns.StdFlrID = floor.StdFlrID
                    '''
    con = sqlite3.connect(dbname)
    section = pd.read_sql(section_sql,con)
    con.close()
    for index,each in section.iterrows():
        section.loc[index,['b','h']] = [int(e) for e in each.ShapeVal.split(',')[1:3]]
    section[['b','h']] = section[['b','h']].astype(np.int64)
    return(section)


def get_dsn(dbname):
    dsn_sql = '''
                select
                seg.ID as ID, seg.FLrNo as floor, dsn.AsDsnT as AsDsnT, 
                dsn.AsDsnB as AsDsnB, dsn.AsRatio as AsRatio, joint.Coord as coord
                from
                tblColSeg as seg
                inner join
                tblRCColDsn dsn
                on seg.ID = dsn.ID
                INNER JOIN
                tblJoint as joint
                on seg.Jt2 = joint.ID
                '''
    con = sqlite3.connect(dbname)
    dsn = pd.read_sql(dsn_sql,con)
    con.close()
    for index,each in dsn.iterrows():
        t = np.array(each.AsDsnT.split(','), dtype=float)
        b = np.array(each.AsDsnB.split(','), dtype=float)
        As = np.maximum(t,b)
        dsn.loc[index,['c_As','b_As','h_As','bs_As','hs_As']] = As
        coord = np.array(each.coord.split(','), dtype=float)
        dsn.loc[index,['X','Y','Z']] = coord
        As_ratio = np.array(each.AsRatio.split(','), dtype=float)
        dsn.loc[index, ['min_As_ratio', 'max_As_ratio', 'min_stirrup_Vol_As_ratio']] = As_ratio
    dsn['all_As'] = 2 * (dsn.b_As + dsn.h_As) - 4 * dsn.c_As
    return(dsn)

def get_col_As_section_info(dbs_path):
    section = get_setion(dbs_path + '/dtlmodel.ydb')
    dsn = get_dsn(dbs_path + '/dtlCalc.ydb')
    info = pd.merge(section, dsn, on=['floor', 'X', 'Y'])
    return info

