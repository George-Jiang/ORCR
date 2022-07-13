# ORCR: Operations Research for Column Rebar

#### Optimize concrete column rebar using MINLP
#### 基于MINLP混合整数非线性规划优化混凝土柱的纵筋
- 求解器：SCIP
- requirements: pyscipopt, numpy

#### 简介
根据运筹学中的线性规划方法，对混凝土柱的钢筋进行优化，给定柱b边和h边配筋的计算值，自动求解b边、h边、角筋的实配钢筋。

由于钢筋直径和各边数量在满足计算值的情况下，可以出现无数种组合，以往的工程实践都是follow your heart，并没有给出全局最优解。

利用线性规划的原理，可快速求出，满足钢筋计算值约束的情况下，总配筋量最小的全局最优解。

相较于盈建科YJK等自动配筋的结果，利用本程序优化后，平均水平上，受力性能可提升10%，总钢筋用量可下降20%，即利用更少的材料实现更好的受力性能。

#### 数学建模
$$
\min z = all\_As
$$

$$
s.t.
\left\{
	\begin{align}
		b\_A > b\_As \\
		h\_A > h\_As \\
		c\_A > c\_As \\
		\sum b\_rebar\_co = 1 \\
		\sum h\_rebar\_co = 1 \\
		\sum c\_rebar\_co = 1 \\
		50 \leq nt \leq 300 \\
		pt \geq pt\_min \\
		pt \geq bd,cd,hd \\
		pt \leq 50
	\end{align}
\right.
$$

$nt$ 为net_space钢筋净间距

$pt$ 为protection_thickness钢筋保护层厚度

#### 使用方法
```python
from orcr import optimize_column_rebar
bn,bd,hn,hd,cd,pt,b_nt,h_nt = optimize_column_rebar(b,h,
                                                    b_As_calc,h_As_calc,c_As_calc,
                                                    stirrup_d=12,pt_min=20,
                                                    bn_input=None,hn_input=None)
#输入
    #b,b边截面尺寸
    #h,h边截面尺寸
    #b_As_calc,b边配筋计算值
    #h_As_calc,h边配筋计算值
    #c_As_calc,角筋配筋计算值
    #stirrup_d,箍筋直径
    #pt_min,钢筋保护层最小厚度
    #bn_input,b边钢筋根数,默认为None,即程序自动判断
    #hn_input,h边钢筋根数,默认为None,即程序自动判断
#输出
    #bn,b边钢筋根数
    #bd,b边钢筋直径
    #hn,h边钢筋根数
    #hd,h边钢筋直径
    #cd,角筋钢筋直径
    #pt,protection_thickness,钢筋保护层厚度
    #b_nt,b边钢筋净距
    #h_nt,h边钢筋净距


###批量处理功能，由ColumnRebarOptimizer类实现
from orcr import ColumnRebarOptimizer
model = ColumnRebarOptimizer()
model.generate_from_excel(excel_filename)
model.optimize()
model.compare()
model.to_excel(filename)
```

#### 备注
`bn_input,hn_input` 
- 若为None，则此问题为MINLP问题，即混合整数非线性规划，求解时间约为0.15s，为MIP问题的10倍左右
- 若为整数，则此问题为MIP问题，即混合整数线性规划，求解时间约为0.02s

### to do list
- 增加CAD图纸生成功能


### change log
#### 2022-07-12
- 增加约束条件
- 钢筋间距约束
- 角筋配筋量约束
- 增加批量处理功能，由ColumnRebarOptimizer类实现
