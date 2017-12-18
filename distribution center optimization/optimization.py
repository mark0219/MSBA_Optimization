'''
##########Data Preperation##########
'''
import MySQLdb as mySQL

db = mySQL.connect(user = 'root', 
                   passwd = '****', 
                   host = 'localhost', 
                   db = 'optifinal')
cur = db.cursor()
cur.execute('select * from mileage')
db.commit()
mileage = cur.fetchall()

cur = db.cursor()
cur.execute('select * from dc')
db.commit()
dc = cur.fetchall()

cur = db.cursor()
cur.execute('select * from store')
db.commit()
store = cur.fetchall()

dc_store = []
k = 0
for i in range(len(dc)):
    row_temp = []
    for j in range(len(store)):
        row_temp.append(mileage[j + k][2])
    dc_store.append(row_temp)
    k = k + len(row_temp)

capacity = []
for i in range(len(dc)):
    capacity.append(dc[i][1])

requirements = []
for i in range(len(store)):
    requirements.append(store[i][1])

'''
##########Gurobi Optimization##########
'''
from gurobipy import *

m = Model("Transportation Prototype")              
m.ModelSense = GRB.MINIMIZE
m.setParam('TimeLimit',7200)

#Setting up decision variables
supply = []
decision_bi = []     
for i in range(len(capacity)):
    row_temp_s = []
    row_temp_d = []
    for j in range(len(requirements)):
        row_temp_s.append(m.addVar(vtype=GRB.INTEGER, name='dc'+str(i)+'_st'+str(j), lb=0.0))
        row_temp_d.append(m.addVar(vtype=GRB.BINARY, name='dc'+str(i)+'_st'+str(j)+'_1/0', lb=0.0))
    supply.append(row_temp_s)
    decision_bi.append(row_temp_d)

m.update()

#Setting up constraints
store_demand = []               #Store demand depending on supply decision
for i in range(len(capacity)):
    row_temp = []
    for j in range(len(requirements)):
        row_temp.append(requirements[j] * decision_bi[i][j])
    store_demand.append(row_temp)

for i in range(len(capacity)):      #Regional supply <= capacity
    m.addConstr(quicksum(supply[i][j] * 1 for j in range(len(requirements))), GRB.LESS_EQUAL, 12000, 'Supply <= Capacity')

for i in range(len(capacity)):      #Store supply >= store demand, if exists
    for j in range(len(requirements)):
        m.addConstr(supply[i][j], GRB.GREATER_EQUAL, store_demand[i][j], 'Supply the store if demand exists')

for i in range(len(requirements)):      #Uniqueness for store supplier
    row_temp = []
    for j in range(len(capacity)):
        row_temp.append(decision_bi[j][i])
    m.addConstr(quicksum(row_temp[k] * 1 for k in range(len(capacity))), GRB.EQUAL, 1, 'Each store can only be supplied by one dc')

for i in range(len(capacity)):      #Regional supply >= regional demand
    m.addConstr(quicksum(store_demand[i][j] * 1 for j in range(len(capacity))), GRB.LESS_EQUAL, quicksum(supply[i][j] * 1 for j in range(len(capacity))), 'Regional supply >= regional demand')

m.update()

#Setting up objective function
m.setObjective(quicksum(dc_store[i][j] * supply[i][j] for i in range(len(capacity)) for j in range(len(requirements))) * 0.75 + 
               quicksum(supply[i][j] * 1 for i in range(len(capacity)) for j in range(len(requirements))) * 200, GRB.MINIMIZE)

m.update()
m.optimize()

'''
##########Dumping Result into DB##########
'''
result_dc = []
result_st = []
for i in range(0, 22000, 2):
    if m.getVars()[i].x > 0:
        value = m.getVars()[i].varname
        value_split = value.split('_')
        result_dc.append(int(value_split[0].strip('dc')))
        result_st.append((value_split[1].strip('st')))

for i in range(len(result_dc)):
    cur.execute("""insert into results value (%s, %s)""", (result_dc[i], result_st[i]))
    db.commit()










