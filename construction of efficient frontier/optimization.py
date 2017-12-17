'''
##########Data Preparation Part##########
'''
import MySQLdb as mySQL

#Hooking up with MySql
db = mySQL.connect(user = 'root', 
                   passwd = '****', 
                   host = 'localhost', 
                   db = 'nasdaq')
cur = db.cursor()
cur.execute('select * from cov')
db.commit()
res = cur.fetchall()

#Populating covariance matrix, or Q. 

k = 0
for i in range(1158):
    temp_list = []
    for j in range(1158):
        temp_list.append(res[j + k][2])
    var_covar_mtx.append(temp_list)
    k = k + len(temp_list)

#Populating return vector
cur.execute('select * from ret')
db.commit()
res_ret = cur.fetchall()
ret_list = list()
for row in res_ret:
    ret_list.append(row[1])

'''
##########Gurobi Optimization Part##########
'''
from gurobipy import *
#Both min and max variance are found in R by calculating the variance of each stock,
#so that at least we will know where to start and where to stop when iterating the loop
#to find the risk - return combination.

min_var = 0.001019543
max_var = 0.4480711
var_inc = (max_var - min_var) / 50
max_risk = min_var
risk_return_combs = []

#Declairing model and problem type
m = Model("portfolio")              
m.ModelSense = GRB.MINIMIZE
m.setParam('TimeLimit',7200)        

#Setting up decision vars, weights
weights = []         
for i in range(len(var_covar_mtx)):
    weights.append(m.addVar(vtype=GRB.CONTINUOUS,name='w'+str(i), lb=0.0))
m.update()

#Adding initial constraints: weights and initialized maximum allowable portfolio risk
m.addConstr(quicksum(weights[i] for i in range(len(weights))), GRB.EQUAL, 1.0, 'Weight integrity')
m.addConstr(quicksum(weights[i] * var_covar_mtx[i][j] * weights[j] for i in range(len(weights)) for j in range(len(weights))), GRB.LESS_EQUAL, max_risk, 'max_risk')
m.update()

#Optimizing iteratively by substituting different constraint
for i in range(50):

    pair_temp = []

    m.setObjective(quicksum(ret_list[i] * weights[i] for i in range(len(weights))), GRB.MAXIMIZE)
    m.update()
    m.optimize()
    
    pair_temp.append(max_risk)
    pair_temp.append(m.objVal)
    risk_return_combs.append(pair_temp)
    
    m.remove(m.getQConstrs())
    m.update()
    
    max_risk = max_risk + var_inc
    m.addConstr(quicksum(weights[i] * var_covar_mtx[i][j] * weights[j] for i in range(len(weights)) for j in range(len(weights))), GRB.LESS_EQUAL, max_risk, 'max_risk')
    m.update()
    

'''
##########Dumping Data into DB##########
'''
for i in range(len(risk_return_combs)):
    cur.execute("""insert into portfolio value (%s, %s)""", (risk_return_combs[i][0], risk_return_combs[i][1]))
    db.commit()

