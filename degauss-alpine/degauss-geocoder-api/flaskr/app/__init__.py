import os
import sys
import uuid

from flask import Flask, Request, request, jsonify
from .modules.response import ok, bad_request, forbidden, not_found, server_error
from .modules.degauss import DegaussConnector

app = Flask(__name__)
degauss = DegaussConnector() 

#########################################
# Routes
#########################################
@app.route('/degausslatlong', methods=['GET'])
def degausslatlong():
    try:
        address = request.args.get('q')
        
        if not address:
            return bad_request()

        data = degauss.degauss_lat_long(address)
        if data:
            return ok(data)

        return not_found()

    except Exception as ex:
        sys.stderr.write(f'Error: {ex}\n')
        return server_error()
