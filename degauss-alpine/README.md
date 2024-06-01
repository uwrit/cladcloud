# Turning the R Degauss Geocoder implementation into an API for servicing a single address

Pulling from here:  https://github.com/degauss-org/geocoder/tree/master

Slapping a copy of the Flask API implementation on top of that based on UW Geocoder approach.

Here we are also adapting the Ubuntu impementation into an Alpine approach.


## Usage 

```
$ curl http://cladgeocoder.rit.uw.edu:50008/degausslatlong?q=1410+NE+Campus+Parkway%2c+Seattle%2c+WA+98195

[{"street":"NE Campus Pkwy","zip":"98195","city":"Seattle","state":"WA","lat":47.656234,"lon":-122.315577,"fips_county":"53033","score":0.806,"prenum":"","number":"1198","precision":"street"}]

```





