import json
from flask import Flask, jsonify, request
import numpy as np


c, f, t, a_f, a_b = None, None, None, None, None
app = Flask(__name__)


@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({'name': 'Zihao',
                    'content': 'What\'s up bro'})# test connection


@app.route('/search', methods=['GET'])
def search():
    return jsonify({'result': 'success',
                    'consistency': c,
                    'framework': f,
                    'timing': t,
                    'acceleration_forehand': a_f['score'],
                    'acceleration_backhand': a_b['score']})# return the result of evaluation


@app.route('/update_cf', methods=['PUT'])
def update_cf():
    temp1 = json.loads(request.data)#receive the result from client
    global c,f
    c,f = temp1['consistency'], temp1['framework']#update  consistency and framework
    return jsonify({'result': 'success',
                    'consistency': c,
                    'framework': f})


@app.route('/update_t', methods=['PUT'])
def update_t():
    global t
    t = json.loads(request.data)['timing']#update  timing
    return jsonify({'result': 'success',
                    'timing': t})
                    
@app.route('/update_a_sb', methods=['PUT'])
def update_a_sb():#shakehand backhand for part 3
    global a_b
    temp2 = np.array(json.loads(request.data)['input'])
    extract = int(len(temp2)/2)
    temp3 = []
    for i in range(extract):
        temp3.append(np.sqrt(temp2[2*i]**2 + temp2[2*i+1]**2))
    median_xy = np.median(temp3)
    if median_xy > 1.24*1.2:
        a_b = {'state':'Fast', 'score':2}
    elif median_xy < 1.24*0.7:
        a_b = {'state':'Slow', 'score':1}
    else:
        a_b = {'state':'Perfect', 'score':3}
    print(a_b)#update backhand acceleration 
    return jsonify({'result': 'success',
                    'state': a_b['state'],'score': a_b['score']})# return backhand state and backhand score

@app.route('/update_a_pb', methods=['PUT'])
def update_a_pb():#penhold backhand for part 3
    global a_b
    temp2 = np.array(json.loads(request.data)['input'])
    extract = int(len(temp2)/2)
    temp3 = []
    for i in range(extract):
        temp3.append(np.sqrt(temp2[2*i]**2 + temp2[2*i+1]**2))
    median_xy = np.median(temp3)
    if median_xy > 1.22*1.2:
        a_b = {'state':'Fast', 'score':2}
    elif median_xy < 1.22*0.7:
        a_b = {'state':'Slow', 'score':1}
    else:
        a_b = {'state':'Perfect', 'score':3}
    print(a_b)#update backhand acceleration 
    return jsonify({'result': 'success',
                    'state': a_b['state'],'score': a_b['score']})# return backhand state and backhand score
                    

@app.route('/update_a_sf', methods=['PUT'])
def update_a_sf():#shakehand forehand for part 3
    global a_f
    temp4 = np.array(json.loads(request.data)['input'])
    print(temp4)
    extract = int(len(temp4)/2)
    temp5 = []
    for i in range(extract):
        temp5.append(np.sqrt(temp4[2*i]**2 + temp4[2*i+1]**2))
    median_xy = np.median(temp5)
    if median_xy > 1.68*1.3:
        a_f = {'state':'Fast', 'score':2}
    elif median_xy < 1.68*0.7:
        a_f = {'state':'Slow', 'score':1}
    else:
        a_f = {'state':'Perfect', 'score':3}
    print(a_f)#update forehand acceleration 
    return jsonify({'result': 'success',
                    'state': a_f['state'],'score': a_f['score']})# return forehand state and backhand score

@app.route('/update_a_pf', methods=['PUT'])
def update_a_pf():#penhold forehand for part 3
    global a_f
    temp4 = np.array(json.loads(request.data)['input'])
    print(temp4)
    extract = int(len(temp4)/2)
    temp5 = []
    for i in range(extract):
        temp5.append(np.sqrt(temp4[2*i]**2 + temp4[2*i+1]**2))
    median_xy = np.median(temp5)
    if median_xy > 1.68*1.3:
        a_f = {'state':'Fast', 'score':2}
    elif median_xy < 1.68*0.7:
        a_f = {'state':'Slow', 'score':1}
    else:
        a_f = {'state':'Perfect', 'score':3}
    print(a_f)#update forehand acceleration 
    return jsonify({'result': 'success',
                    'state': a_f['state'],'score': a_f['score']})#return penhold forehand state and scores

@app.route('/reset', methods=['DELETE'])
def reset():
    global c,f,t,a_b,a_f
    c, f, t, a_b, a_f = None, None, None, None, None# reset all data
    return jsonify({'result': 'success'})


if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 5002)