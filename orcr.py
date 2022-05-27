from pyscipopt import Model
import numpy as np


def optimize_column_rebar(b_As_calc, h_As_calc, bn_input=None, hn_input=None):
    #输入
    #b_As_calc,b边配筋计算值
    #h_As_calc,h边配筋计算值
    model = Model()

    rebar_list = np.array([12,14,16,18,20,22,25,28,30,32,35])
    #可选钢筋的单根面积(cm2)
    rebar_area_list = np.pi * rebar_list **2 /4 /100

    #b、h边钢筋数量
    bn = model.addVar('bn', vtype='I')
    hn = model.addVar('hn', vtype='I')
    all_As = model.addVar('all_As')

    #选筋0-1变量
    b_rebar_co = np.array([model.addVar('b_rebar_d' + str(e), vtype = 'B') for e in rebar_list])
    h_rebar_co = np.array([model.addVar('h_rebar_d' + str(e), vtype = 'B') for e in rebar_list])
    c_rebar_co = np.array([model.addVar('c_rebar_d' + str(e), vtype = 'B') for e in rebar_list])

    #钢筋面积
    bA = b_rebar_co.dot(rebar_area_list)
    hA = h_rebar_co.dot(rebar_area_list)
    cA = c_rebar_co.dot(rebar_area_list)

    #钢筋的直径
    bd = b_rebar_co.dot(rebar_list)
    hd = h_rebar_co.dot(rebar_list)
    cd = c_rebar_co.dot(rebar_list)

    #b、h边钢筋量
    b_As = 2*cA + bn * bA
    h_As = 2*cA + hn * hA

    #添加约束

    #添加单个类型选筋0-1变量约束
    model.addCons(sum(b_rebar_co) == 1)
    model.addCons(sum(h_rebar_co) == 1)
    model.addCons(sum(c_rebar_co) == 1)

    #添加钢筋量约束
    model.addCons(b_As >= b_As_calc)
    model.addCons(h_As >= h_As_calc)

    #添加单边钢筋个数约束，以后需改成根据规范规则的约束
    if bn_input == None:
        model.addCons(bn >= 1)
    else:
        model.addCons(bn == bn_input)
    if hn_input == None:
        model.addCons(hn >= 1)
    else:
        model.addCons(hn == hn_input)
    
    #如果是预制柱需要的角部配筋，可以调整钢筋个数输入参数bn_input=2,hn_input=2

    #以约束方式添加目标函数，SCIP不允许目标函数为非线性，只能以约束的形式输入
    model.addCons(all_As == 4*cA + 2*bn*bA + 2*hn*hA)

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
        #print('结果:')
        #print('全部配筋梁(cm2):', obj)
        #print('b边钢筋量:', solve[b_As])
        #print('h边钢筋量:', solve[h_As])
        #print('b:', str(bn_result) + 'D' + str(bd_result))
        #print('h:', str(hn_result) + 'D' + str(hd_result))
        #print('c:', '4D' + str(cd_result))
        return(bn_result,bd_result,hn_result,hd_result,cd_result)

    else:
        #print('无法找到合适的解')
        return(None)




