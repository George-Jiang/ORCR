from pyscipopt import Model
import numpy as np


def optimize_column_rebar(
        b, h,
        b_As_calc, h_As_calc, c_As_calc,
        stirrup_d=8, pt_min=20, min_As_rate=None,
        bn_input=None, hn_input=None):
    # 输入
    # b_As_calc,b边配筋计算值
    # h_As_calc,h边配筋计算值
    model = Model()

    rebar_list = np.array([12, 14, 16, 18, 20, 22, 25, 28, 30, 32, 36, 40])
    # 可选钢筋的单根面积(mm2)
    rebar_area_list = np.pi * rebar_list ** 2 / 4

    ###添加变量

    # b、h边钢筋数量变量
    bn = model.addVar('bn', vtype='I')
    hn = model.addVar('hn', vtype='I')
    all_As = model.addVar('all_As')
    As_rate = all_As / b / h

    # 选筋0-1变量
    b_rebar_co = np.array([model.addVar('b_rebar_d' + str(e), vtype='B') for e in rebar_list])
    h_rebar_co = np.array([model.addVar('h_rebar_d' + str(e), vtype='B') for e in rebar_list])
    c_rebar_co = np.array([model.addVar('c_rebar_d' + str(e), vtype='B') for e in rebar_list])

    # 保护层厚度变量,箍筋外皮的保护层厚度
    pt = model.addVar('pt', vtype='C')
    # 纵筋外皮的保护层厚度，为箍筋保护层厚度+箍筋直径
    pt_rebar = pt + stirrup_d

    # 钢筋面积
    bA = b_rebar_co.dot(rebar_area_list)
    hA = h_rebar_co.dot(rebar_area_list)
    cA = c_rebar_co.dot(rebar_area_list)

    # 钢筋的直径
    bd = b_rebar_co.dot(rebar_list)
    hd = h_rebar_co.dot(rebar_list)
    cd = c_rebar_co.dot(rebar_list)

    # b、h边钢筋量
    b_As = 2 * cA + bn * bA
    h_As = 2 * cA + hn * hA
    c_As = cA

    # 钢筋净间距nt:net_space
    b_nt = (b - 2 * pt - 2 * cd - 2 * stirrup_d - bn * bd) / (bn + 1)
    h_nt = (h - 2 * pt - 2 * cd - 2 * stirrup_d - hn * hd) / (hn + 1)

    ###添加约束

    # 添加单个类型选筋0-1变量约束
    model.addCons(sum(b_rebar_co) == 1)
    model.addCons(sum(h_rebar_co) == 1)
    model.addCons(sum(c_rebar_co) == 1)

    # 添加钢筋量约束
    model.addCons(b_As >= b_As_calc)
    model.addCons(h_As >= h_As_calc)
    model.addCons(c_As >= c_As_calc)

    # 添加单边钢筋个数约束，以钢筋净间距为约束50<= nt <=300
    if bn_input is None:
        model.addCons(b_nt >= 50)
        model.addCons(b_nt <= 300)
    else:
        model.addCons(bn == bn_input)
    if hn_input is None:
        model.addCons(h_nt >= 50)
        model.addCons(h_nt <= 300)
    else:
        model.addCons(hn == hn_input)

    #最小配筋率约束
    if min_As_rate is not None:
        model.addCons(As_rate >= min_As_rate)

    # 添加保护层厚度约束
    model.addCons(pt >= pt_min)
    model.addCons(pt_rebar >= bd)
    model.addCons(pt_rebar >= hd)
    model.addCons(pt_rebar >= cd)
    model.addCons(pt <= 50)

    # 以约束方式添加目标函数，SCIP不允许目标函数为非线性，只能以约束的形式输入
    model.addCons(all_As == 4 * cA + 2 * bn * bA + 2 * hn * hA)

    model.setObjective(all_As)

    model.optimize()

    if model.getNSols() > 0:
        solve = model.getBestSol()
        obj = model.getObjVal()
        bn_result = round(solve[bn])
        hn_result = round(solve[hn])
        bd_result = round(solve[bd])
        hd_result = round(solve[hd])
        cd_result = round(solve[cd])
        pt_result = round(solve[pt])
        b_nt_result = round(
            (b - 2 * pt_result - 2 * cd_result - 2 * stirrup_d - bn_result * bd_result) / (bn_result + 1))
        h_nt_result = round(
            (h - 2 * pt_result - 2 * cd_result - 2 * stirrup_d - hn_result * hd_result) / (hn_result + 1))
        # print('结果:')
        # print('全部配筋梁(mm2):', obj)
        # print('b边钢筋量:', solve[b_As])
        # print('h边钢筋量:', solve[h_As])
        # print('b:', str(bn_result) + 'D' + str(bd_result))
        # print('h:', str(hn_result) + 'D' + str(hd_result))
        # print('c:', '4D' + str(cd_result))
        return ([bn_result, bd_result, hn_result, hd_result, cd_result, pt_result, b_nt_result, h_nt_result])

    else:
        print('无法找到合适的解')
        return (None)
