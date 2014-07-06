import json
import psycopg2
from bottle import route, run, request


def getPolygon(polygon):
    polygonJSON = json.loads(polygon)
    if 'features' in polygonJSON:
        no_of_polygons = len(polygonJSON['features'])
        if no_of_polygons > 1:
            finalPolygon = "MULTIPOLYGON((("
            for feature in polygonJSON['features']:
                for obj in feature['geometry']['coordinates']:
                    for point in obj:
                        longitude = point[0]
                        latitude = point[1]
                        finalPolygon += '%s %s,' % (longitude, latitude)
                finalPolygon = finalPolygon[:-1]
                finalPolygon += ')),(('
            finalPolygon = finalPolygon[:-3]
            finalPolygon += ")"
        else:
            finalPolygon = "POLYGON(("
            for feature in polygonJSON['features']:
                for item in feature['geometry']['coordinates']:
                    for point in item:
                        longitude = point[0]
                        latitude = point[1]
                        vertex = "%s %s" % (longitude, latitude)
                        finalPolygon += "%s," % (vertex,)
                finalPolygon = finalPolygon[:-1]
                finalPolygon += "))"
    else:
        finalPolygon = "POLYGON(("
        for point in polygonJSON['coordinates'][0]:
            longitude = point[0]
            latitude = point[1]
            vertex = "%s %s" % (longitude, latitude)
            finalPolygon += "%s," % (vertex,)
        finalPolygon = finalPolygon[:-1]
        finalPolygon += "))"
    return finalPolygon


#This function returns the crime happened within the given polygon
def pointInPolygon(walkshed):
    import config

    connection_string = config.conf()
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()
    polygon = getPolygon(walkshed)
    selectQuery = "SELECT id, ST_AsText(crime_location), crime_time, crime_type FROM cps_crime_data.crime_data WHERE ST_Within(crime_location, ST_GeomFromText(%s, 4326));"
    parameters = [polygon]
    cur.execute(selectQuery, parameters)
    rows = cur.fetchall()
    if len(rows) > 0:
        result_json = '{"type": "FeatureCollection", "features": ['
        for i in xrange(len(rows)):
            id = rows[i][0]
            location = rows[i][1]
            location = location[6:].split(' ')
            longitude = location[0]
            latitude = location[1][:-1]
            location = "[%s,%s]" % (longitude, latitude)
            time = rows[i][2]
            time = "%s-%s-%s %s:%s:00" % (time.year, time.month, time.day, time.hour, time.minute)
            type = rows[i][3]
            result_json += '{"type": "Feature","geometry": {"type": "Point", "coordinates":%s}, "properties": {"id": %s, "time": "%s","type": "%s"}},' % (
                location, id, time, type)
        result_json = result_json[:-1]
        result_json += ']}'
    else:
        result_json = '"NULL"'
    conn.commit()
    cur.close()
    conn.close()
    return result_json


@route('/crime')
def service():
    polygon = request.GET.get('walkshed', default=None)
    if polygon is not None:
        return pointInPolygon(polygon)


run(host='0.0.0.0', port=9366, debug=True)

#http://127.0.0.1:9366/crime?walkshed={"type": "FeatureCollection", "features": [{"type": "Feature","geometry": {"type":"Polygon","coordinates":[[[-114.123550664,51.037806666],[-114.122217395,51.0386516217],[-114.120788316,51.0395693061],[-114.120692143,51.0396207204],[-114.117913083,51.0409935348],[-114.1160728,51.0414704],[-114.115949,51.0414799],[-114.1139254,51.0415688],[-114.1124143,51.0412835],[-114.1123592,51.0412621],[-114.108643812,51.0398476899],[-114.108009238,51.0394725745],[-114.103865832,51.0378159316],[-114.104239101,51.0375437925],[-114.108110204,51.0345569],[-114.109448719,51.0337095],[-114.110836744,51.0328753632],[-114.111395757,51.032616866],[-114.1136487,51.0340556434],[-114.1179527,51.035325],[-114.119312915,51.0351592874],[-114.120812567,51.0360643617],[-114.121133969,51.0362614574],[-114.123550664,51.037806666]]]}},{"type": "Feature","geometry": {"type":"Polygon","coordinates":[[[-114.1329929,51.0653258],[-114.132508867,51.0661349087],[-114.131810449,51.0649222514],[-114.131844868,51.0649314777],[-114.132634884,51.0651432456],[-114.1327526,51.0651748],[-114.13285896,51.0652416344],[-114.1329929,51.0653258]]]}},{"type": "Feature","geometry": {"type":"Polygon","coordinates":[[[-114.1009165,51.0488906],[-114.1040593,51.0490814],[-114.105805554113,51.0491056872064],[-114.107161576783,51.0489233665647],[-114.11157,51.04815],[-114.111898635,51.0481264753],[-114.115020468142,51.0499909470258],[-114.115184718695,51.0500103260138],[-114.1175707,51.0498049656],[-114.118771226,51.0502342203],[-114.119756059664,51.0509540132883],[-114.122270068842,51.0526329290899],[-114.125129,51.053914],[-114.129204,51.055165],[-114.133781,51.056393],[-114.134421528,51.0565416021],[-114.134512974,51.0573769433],[-114.133186713,51.0581183182],[-114.132385616364,51.0583857729279],[-114.132635179,51.0598409881],[-114.13005635,51.0609289095],[-114.1254683,51.0591547],[-114.1253905,51.0590982],[-114.125389733,51.0590485599],[-114.125744167,51.0586962278],[-114.12644842,51.0582529553],[-114.127042014576,51.0578803892395],[-114.12699768893,51.0578525718375],[-114.12537635,51.0579407119],[-114.124441581,51.0573653861],[-114.124188311224,51.0572121988609],[-114.12397229,51.0573653285],[-114.12326797,51.0578054941],[-114.122929102,51.0580166709],[-114.122528292,51.0582544218],[-114.121799599,51.0586897305],[-114.120251603996,51.0598477594681],[-114.120889846,51.0599018177],[-114.12140751,51.0607842],[-114.121261898729,51.061141102109],[-114.12201057,51.0612504665],[-114.125173885,51.0626435529],[-114.125841258,51.0635676189],[-114.124829053,51.0643308806],[-114.125769855239,51.0684086839971],[-114.126711802617,51.0686728041712],[-114.129129446,51.0679803498],[-114.131160245,51.0690559405],[-114.133756054,51.07151957],[-114.133404718,51.0723505264],[-114.132515874,51.0742496165],[-114.132418941,51.0743847314],[-114.131614322,51.0750671838],[-114.13056368,51.075851151],[-114.1302125,51.0759563],[-114.128478102,51.0764544567],[-114.1277298,51.0765914],[-114.127303985,51.0765918094],[-114.1272403,51.0765653],[-114.124383679,51.0752200225],[-114.124034759,51.0750755123],[-114.1209573,51.0721611],[-114.118613929,51.0739653071],[-114.118413676,51.0739692894],[-114.116576612,51.0710392359],[-114.118080835,51.069187687],[-114.118327659923,51.0686246882971],[-114.118048752,51.0679525888],[-114.1180429,51.0678746],[-114.117876381468,51.0640382842574],[-114.117735984,51.0640925314],[-114.1131162,51.0622073],[-114.1129392,51.0620646],[-114.1118298,51.0600444],[-114.112453726079,51.0595959192811],[-114.110783019819,51.0593148805409],[-114.110151936,51.0596484792],[-114.108788568674,51.0603915083195],[-114.1071042,51.0616758515],[-114.106275203,51.0623458832],[-114.105716295576,51.0621201667657],[-114.104879651,51.062739498],[-114.102000608608,51.0625153120585],[-114.101694477,51.0626964377],[-114.099819915,51.0639029456],[-114.098337091,51.0643950937],[-114.095354388,51.0664199243],[-114.094768291,51.0664927751],[-114.094005806,51.0663494891],[-114.091433249,51.0644302944],[-114.091338057,51.0629621742],[-114.0880542,51.0595524],[-114.085808,51.058723],[-114.085277706,51.0583519592],[-114.083984445,51.0569930542],[-114.084284041,51.0565586212],[-114.085922269,51.0553805894],[-114.087295953,51.0544695361],[-114.089714068,51.0529418436],[-114.090196385,51.0526453929],[-114.090237928243,51.0526197928733],[-114.090141071,51.052508144],[-114.090444945,51.0522349009],[-114.094688996,51.049615568],[-114.095639167,51.0492165233],[-114.098223,51.0489835],[-114.0995548,51.0488845],[-114.1009165,51.0488906]]]}}]}
#http://127.0.0.1:9366/crime?walkshed={"type": "FeatureCollection", "features": [{"type": "Feature","geometry": {"type":"Polygon","coordinates":[[[-114.007180793,51.0454607242],[-114.006408355,51.0453024406],[-114.006089,51.045237],[-114.005247829,51.045122489],[-114.0047888,51.04506],[-114.0037093,51.0449802],[-114.003291674,51.044972313],[-114.006362915,51.0453872681],[-114.007180793,51.0454607242]]]}},{"type": "Feature","geometry": {"type":"Polygon","coordinates":[[[-114.061788953,51.0454902688],[-114.061565663,51.0474074372],[-114.060428264,51.0480752899],[-114.059356933,51.0473453959],[-114.059423243,51.0454170308],[-114.060649426,51.044699243],[-114.061788953,51.0454902688]]]}},{"type": "Feature","geometry": {"type":"Polygon","coordinates":[[[-114.056678772,51.046257019],[-114.05562462,51.0472335139],[-114.055500609,51.0473044777],[-114.055387964,51.0472269103],[-114.055574293,51.0462166233],[-114.056678772,51.046257019]]]}},{"type": "Feature","geometry": {"type":"Polygon","coordinates":[[[-114.046870567,51.0497105764],[-114.046841159,51.0508111022],[-114.044536077,51.0523827386],[-114.043252564,51.0532534762],[-114.041697338,51.054257254],[-114.039026931,51.0558900581],[-114.038754837,51.0560498245],[-114.038377537,51.0562576245],[-114.037029882,51.0569365837],[-114.0350283,51.0564921],[-114.031964953,51.0567706789],[-114.02987022,51.0565174087],[-114.0288391,51.0547697],[-114.025723748,51.0519576569],[-114.024177284,51.0505784957],[-114.022371508,51.048378281],[-114.021882937,51.0474669205],[-114.026139533,51.0451394472],[-114.029716723,51.0436949883],[-114.032585066,51.0430688257],[-114.0364458,51.0456555],[-114.0369355,51.0458008],[-114.0371281,51.0458566],[-114.0372263,51.0458842],[-114.0373195,51.0459125],[-114.0391232,51.0463075],[-114.0391873,51.0463183],[-114.0399743,51.046452],[-114.0400681,51.0464657],[-114.0401752,51.0464863],[-114.0408188,51.0466467],[-114.0409368,51.046685],[-114.0410213,51.0467243],[-114.0410681,51.0467582],[-114.04444,51.04891],[-114.045725499,51.0492474976],[-114.046870567,51.0497105764]]]}}]}