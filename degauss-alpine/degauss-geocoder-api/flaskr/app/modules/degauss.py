import os

class DegaussConnector:

    def degauss_lat_long(self, var_address):

        str_construct = "ruby /app/geocode.rb '" + var_address + "'"
        result = os.popen(str_construct).read()

        if result is None:
            return None

        return result 

