from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse
import json
from workalendar.registry import registry
from workalendar.exceptions import CalendarError

def get_holidays(start, end):
    errors = []
    items = []
    for code, calendar_class in registry.region_registry.items():
        for year in range(int(start), int(end) + 1):
            #print("`{}` is code for '{}'".format(code, calendar_class.name))
            cal = registry.get_calendar_class(code)
            obj = cal()
            try:
                for hol in obj.holidays(year):
                    items.append(
                        {
                            'iso_code' : code,
                            'location_name' : calendar_class.name,
                            'holiday' : hol[1],
                            'date' : hol[0].isoformat(),
                            'requested_year' : year
                        }
                    )
            except CalendarError as exc:
                errors.append(str(exc))
            except KeyError as exc:
                errors.append(str(exc))
    
    return items, errors

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        #parsed_path = urlparse(self.path)
        parsed_path = urlparse.urlparse(self.path)
        #Get a list of holidays for all countries
        items, errors = get_holidays(
                        urlparse.parse_qs(parsed_path.query)['start'][0],
                        urlparse.parse_qs(parsed_path.query)['end'][0]
                        )
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({
            'items': items,
            'errors': errors
        }).encode())
        return

if __name__ == '__main__':
    server = HTTPServer(('', 8000), RequestHandler)
    server.serve_forever()
