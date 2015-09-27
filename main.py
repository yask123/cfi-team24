from flask import Flask, request, render_template, render_template
from flask import make_response, current_app, abort, jsonify
from datetime import timedelta
from functools import update_wrapper
import urllib
import json
import requests

app = Flask(__name__)

def crossdomain(origin=None, methods=None, headers=None,
        max_age=21600, attach_to_all=True,
        automatic_options=True):
  if methods is not None:
    methods = ', '.join(sorted(x.upper() for x in methods))
  if headers is not None and not isinstance(headers, basestring):
    headers = ', '.join(x.upper() for x in headers)
  if not isinstance(origin, basestring):
    origin = ', '.join(origin)
  if isinstance(max_age, timedelta):
    max_age = max_age.total_seconds()

  def get_methods():
    if methods is not None:
      return methods

    options_resp = current_app.make_default_options_response()
    return options_resp.headers['allow']

  def decorator(f):
    def wrapped_function(*args, **kwargs):
      if automatic_options and request.method == 'OPTIONS':
        resp = current_app.make_default_options_response()
      else:
        resp = make_response(f(*args, **kwargs))
      if not attach_to_all and request.method != 'OPTIONS':
        return resp

      h = resp.headers

      h['Access-Control-Allow-Origin'] = origin
      h['Access-Control-Allow-Methods'] = get_methods()
      h['Access-Control-Max-Age'] = str(max_age)
      if headers is not None:
        h['Access-Control-Allow-Headers'] = headers
      return resp

    f.provide_automatic_options = False
    return update_wrapper(wrapped_function, f)
  return decorator

#------------------------------------------------------------------------------


def getOrder(origin,waypoints):
  origin = origin
  waypoints = '|'.join(waypoints)
  url = 'https://maps.googleapis.com/maps/api/directions/json?origin='+origin+'&destination='+origin+'&waypoints=optimize:true|'+waypoints+'&key=AIzaSyDmFfFmAAJ_9wnCsaz6oOGvyUeMis9BmkI'
  print url
  data = requests.get(url).json()
  return data['routes'][0]['waypoint_order']

def getDirectionURLs(names,waypoints):
  result = []
  for i in xrange(len(waypoints)-1):
    source = waypoints[i]
    destination = waypoints[i+1]
    name = names[i+1]
    url = 'https://www.google.co.in/maps/dir/'+source+'/'+destination
    # print url
    result.append([name,url])
  return result

@app.route('/')
def map():
  return render_template('map.html', name='map')

@app.route('/map', methods=['GET'])
@crossdomain(origin='*')
def calculate():
  if request.method == 'GET':
    print 'f'
    origin_ = request.args['source']
    origin = urllib.quote_plus(origin_)
    waypoints_ = request.args.getlist('waypoints[]')
    waypoints = [ urllib.quote_plus(i) for i in waypoints_]
    print waypoints

    # origin = 'Adelaide,SA'
    # waypoints = ['Barossa+Valley,SA','Clare,SA','Connawarra,SA','McLaren+Vale,SA']
    order = getOrder(origin=origin,waypoints=waypoints)
    ordered_waypoints = list(waypoints)
    names = list(waypoints_)
    for i,j in enumerate(order):
      ordered_waypoints[i] = waypoints[j]
      names[i] = waypoints_[j]

    ordered_names = [origin_] + names + [origin_]
    ordered_waypoints = [origin] + ordered_waypoints + [origin]
    # print ordered_waypoints
    result = getDirectionURLs(names=ordered_names,waypoints=ordered_waypoints)
  else:
    print 'no POST baby'
  return render_template('result.html', name='map', result=result)
  return json.dumps(result)

if __name__ == '__main__':
  app.run(port=3000, debug=True)
