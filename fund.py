import pandas as pd
import numpy as np
from scipy.optimize import minimize
from flask import Flask, request, render_template

app = Flask("__name__")

@app.route("/")
def loadPage():
    return render_template('index.html', query="")

def create_data_frame():
    Asset1 = [
        2.75,   # January
        -1.50,  # February
        3.20,   # March
        0.85,   # April
        -3.10,  # May
        1.60,   # June
        4.90,   # July
        -0.75,  # August
        5.25,   # September
        -2.40,  # October
        1.95    # November
    ]
    Asset2 =[
        -2.10,   # January
        1.35,    # February
        -0.85,   # March
        3.40,    # April
        -1.20,   # May
        0.65,    # June
        4.50,    # July (based on the data you provided)
        -2.19,   # August (based on the data you provided)
        1.89,    # September
        -0.70,   # October
        2.55,    # November
    
    ]
    Asset3 =[
        -1.25,  # January
        0.85,   # February
        1.50,   # March
        2.10,   # April
        -0.65,  # May
        3.25,   # June
        1.80,   # July
        -0.90,  # August
        4.50,   # September
        -2.10,  # October
        1.35    # November
    ]
    Asset4 =[
        0.25,   # January
        0.40,   # February
        0.15,   # March
        0.75,   # April
        -0.20,  # May
        0.60,   # June
        0.85,   # July
        0.30,   # August
        1.10,   # September
        -0.10,  # October
        0.50    # November
    ]
    data = {
        'Asset1' : Asset1,
        'Asset2' : Asset2,
        'Asset3' : Asset3,
        'Asset4' : Asset4
    }
    df = pd.DataFrame(data)
    return df

def objective_function(weights, expected_returns):
    return -np.dot(weights.T, expected_returns)  # Negative because we are minimizing

# Define the constraint for portfolio risk
def constraint_risk(weights, cov_matrix, risk_target):
    return risk_target - np.dot(weights.T, np.dot(cov_matrix, weights))

# Define the constraint for weights sum
def constraint_sum(weights):
    return np.sum(weights) - 1



@app.route("/", methods=['POST'])
def predict():
    # n = 0
    # m = 0
    time = request.form['time']
    risk = request.form['risk']
    amount = request.form['amount']
    amount = int(amount)
    # if time == '1 month':
    #     n = 1
    # elif time == '3 month':
    #     n = 3
    # elif time == '12 month':
    #     n = 12

    # if time == '3 year':
    #     m = 3
    # elif time == '5 year':
    #     m = 5

    data = create_data_frame()

    start,end = risk.split('-')
    start = int(start)
    end = int(end)

    if data.empty:
        return render_template('index.html', output1="No data available for the selected time frame.")

    expected_returns = [1.159090909090909, 0.6636363636363636, 0.95, 0.41818181818181815]
    risk_target = end/100
    cov_matrix = data.cov()
    num_assets = len(expected_returns)
    initial_weights = np.ones(num_assets) / num_assets
    bounds = [(0, 1) for _ in range(num_assets)] 
    constraints = [{'type': 'eq', 'fun': constraint_sum},
                {'type': 'ineq', 'fun': constraint_risk, 'args': (cov_matrix, risk_target)}]
    
    result = minimize(objective_function, initial_weights, args=(expected_returns), method='SLSQP', bounds=bounds, constraints=constraints)
    optimal_weights = result.x
    optimal_return = -result.fun 
    o1 = 'Optimal return {returns}'.format(returns = optimal_return*amount)
    p1 = 'Asset1 allocation {pe1}'.format(pe1 = optimal_weights[0]*amount)
    p2 = 'Asset2 allocation {pe2}'.format(pe2 = optimal_weights[1]*amount)
    p3 = 'Asset3 allocation {pe3}'.format(pe3 = optimal_weights[2]*amount)
    p4 = 'Asset4 allocation {pe4}'.format(pe4 = optimal_weights[3]*amount)

    return render_template('index.html', output1=o1,
                           percent1 = p1,
                           percent2 = p2,
                           percent3 = p3,
                           percent4 = p4,
                           amount = amount,
                           risk = risk,
                           time = time)

if __name__ == "__main__":
    app.run(debug=True, port=5002, host = "0.0.0.0")
