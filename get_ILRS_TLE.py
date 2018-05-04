import urllib
from sys import argv, exit
from datetime import datetime
from http.cookiejar import CookieJar
from lxml import html
import urllib.request

ILRS_URL = "https://ilrs.cddis.eosdis.nasa.gov/missions/satellite_missions/current_missions/index.html"

class SatelliteRetriever:
    def __init__(self, config):
        self.last_login = datetime(year=1900, month=1, day=1)
        self.credentials = {
            "identity" : config["username"],
            "password" : config["password"]
        }
        self.DEBUG = config["debug_level"]
        self.CJ = CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.CJ))
        self.lists = {}
    
    def get_ILRS_numbers(self):
        """Retrieve the list of active ILRS satellite catalog numbers."""
        if self.DEBUG >= 2:
            print("SatelliteRetriever: Getting active ILRS catalog numbers.")
        page = urllib.request.urlopen(ILRS_URL)
        txt = page.read()
        table = html.fromstring(txt).get_element_by_id("stations")
        rows = iter(table)
        headers = [col.text for col in next(rows)]
        numbers = []
        for row in rows:
            values = [col.text for col in row]
            ID = values[3].strip()
            if ID=="" or ID=="N/A":
                continue
            numbers.append(int(ID))
        self.lists["ILRS_active"] = {"numbers" : sorted(numbers)}
        return sorted(numbers)

    def log_in(self):
        """Log in to space-track.org and store the cookie (expired in ~2 hours).
        Returns True is the log-in succeeded and False if it failed."""
        
        if self.DEBUG >= 2:
            print("SatelliteRetriever: Logging in...")
            
        data = urllib.parse.urlencode(self.credentials).encode("ascii")
        try:
            response = self.opener.open("https://www.space-track.org/ajaxauth/login", data)
        except urllib.error.HTTPError as e:
            print("SatelliteRetriever: {}".format(str(e)))
            return False
        except urllib.error.URLError as e:
            print("SatelliteRetriever: {}".format(str(e)))
            return False
            
        result = response.read().decode("utf-8")
        if "Failed" in result:
            print("SatelliteRetriever: Login failed!")
            return False
        self.last_login = datetime.now()
        return True

    def download_data(self):
        """Go through all satellite lists and download the orbital elements."""
        
        if self.DEBUG >= 1:
            print("SatelliteRetriever: Downloading data...")
        
        delta = datetime.now() - self.last_login
        if delta.seconds > 5400:
            if self.DEBUG >= 2:
                print("SatelliteRetriever: Log-in expired, retrying...")
            ok = self.log_in()
            if not ok:
                print("SatelliteRetriever: Log-in failed.")
                return False
        for listname in self.lists:
            IDs = self.lists[listname]["numbers"]
            filename = "{}.txt".format(listname)
            query = "/".join([
                "https://www.space-track.org/basicspacedata/query",
                "class/tle_latest/ORDINAL/1",
                "NORAD_CAT_ID/{}".format(",".join([str(id) for id in IDs])),
                "format/3le"
            ])
            if self.DEBUG >= 2:
                print("SatelliteRetriever: Requesting elements for '{}'...".format(listname))
            try:
                response = self.opener.open(query)
            except urllib.error.HTTPError as e:
                print("SatelliteRetriever: {}".format(str(e)))
                return False
            data = response.read().decode("utf-8")
            data = data.replace("\r", "")
            with open(filename, "w") as f:
                if self.DEBUG >= 2:
                    print("SatelliteRetriever: Saving to {}...".format(filename))
                f.write(data)
        return True
                

from Config import spacetrack_config


if __name__=="__main__":
    S = SatelliteRetriever(spacetrack_config)
    S.get_ILRS_numbers()
    S.log_in()
    S.download_data()
