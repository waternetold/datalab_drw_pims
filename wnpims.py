try:
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError

import datetime
import pandas as pd
import ww #temp to hide urls

class API:
    def __init__(self):
        self._logbook = []
        self._log("initialized myself")

    def _log(self, msg):
        """Log a message to the logbook, timekeeping is done in this function

        INPUT
        msg: the message you want to log in string format
        """
        self._logbook.append("%s: %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))

    def _get_request_result(self, url, params, output='pandas'):
        """This function sends a request and return the text of the response. It deals in a uniform way with possible errors.

        INPUT
        url   : url of the website to retrieve data from
        params: a dictionary of parameters
        output: output format of the result (default pandas)

        OUTPUT
        output='pandas' => Pandas DataFrame or None in case of error
        output='raw'    => text or None in case of error
        else            => None

        TODO: implement other formats for the result
        """
        finalurl = url + "?%s" % urlencode(params)

        self._log("starting request to %s" % finalurl)

        req = Request(finalurl)
        try:
            resp = urlopen(Request(finalurl))
        except urllib.error.HTTPError as e:
            self._log("Got statuscode %s" % e.code)
            self._log(e.read())
            return None

        text = resp.read().decode('utf-8')

        if text.find('<title>Error</title>') > -1:
            self._log("Got error status from the server")
            return None

        if output=="pandas":
            return self._response_text_to_pandas(text)
        elif output=="raw":
            return text
        else:
            return None

    def _response_text_to_pandas(self, text):
        """Convert the response text to a pandas DataFrame

        INPUT
        text: the response text

        OUTPUT
        Pandas Dataframe or None in case of error

        NOTES
        Expects the text to be formated like
        column1  column2  column3 ...
        value1   value2   value3 ...
        and seperated by tabs (which is the current format of the server)

        OR text formated as a HTML table"""
        data = []

        if text.find('<table>')<0:
            lines = text.split('\n')
            header = [x.replace('\r','') for x in lines[0].split('\t')]
            for i in range(1,len(lines)):
                args = [x.replace(',', '.').replace('\r', '') for x in lines[i].split('\t')]
                if args[-1]=="Bad":
                    self._log("Got error status on data, probably caused by a wrong tagname")
                    return None
                data.append(args)

            result = pd.DataFrame(data, columns=header)
        else:
            return pd.read_html(text)


        return result

    def get_curr_val(self, tagname):
        """Wrapper on the get current value url

        INPUT
        tagname: tagname according to the available taglist

        OUTPUT
        Pandas dataframe or None in case of error
        """
        url = ww.URL_GET_CURR_VAL
        params = {'tagnaam':tagname}
        return self._get_request_result(url, params)

    def get_trend(self, tagname, alist, start, end, interval=1, interval_unit='dagen', calc='actual'):
        """Wrapper on the get trend url

        INPUT
        tagname      : tagname according to the available taglist (wildcards available)
        alist        : TODO, wat betekent dit?
        start        : start date (datetime)
        end          : end date (datetime)
        interval     : interval of measurements (default=1)
        interval_unit: unit of the interval (dagen (default), uren, minuten, seconden)
        calc         : type of calculation (actual (default), avg, min, max, int_lin, int_step)

        OUTPUT
        Pandas dataframe or None in case of error
        """
        url = ww.URL_GET_TREND
        sstart = start.strftime("%d-%m-%Y")
        send = end.strftime("%d-%m-%Y")
        params = {'tagnaam':tagname, 'lijst':alist, 'starttijd':sstart, 'eindtijd':send,
        'periode':interval, 'periode eenheid':interval_unit, 'calculatie':calc}
        return self._get_request_result(url, params)

    def get_trend_pivot(self, tagname, alist, start, end, interval=1, interval_unit='dagen', calc='actual', time_axis=1):
        """Wrapper on the get trend pivot url

        INPUT
        tagname      : tagname according to the available taglist (wildcards available)
        alist        : TODO, wat betekent dit?
        start        : start date (datetime)
        end          : end date (datetime)
        interval     : interval of measurements (default=1)
        interval_unit: unit of the interval (dagen (default), uren, minuten, seconden)
        calc         : type of calculation (actual (default), avg, min, max, int_lin, int_step)
        time_axis    : get time axis (default=1)

        OUTPUT
        Pandas dataframe or None in case of error
        """
        url = ww.URL_GET_TREND_PIVOT
        sstart = start.strftime("%d-%m-%Y")
        send = end.strftime("%d-%m-%Y")
        params = {'tagnaam':tagname, 'lijst':alist, 'starttijd':sstart, 'eindtijd':send,
        'periode':interval, 'periode eenheid':interval_unit, 'calculatie':calc, 'tijdsas':time_axis}
        return self._get_request_result(url, params)

    def get_time_val(self, tagname, timestamp):
        """Wrapper on the get time val url

        INPUT
        tagname      : tagname according to the available taglist (wildcards available)
        timestamp    : datetime of the value

        OUTPUT
        Pandas dataframe or None in case of error
        """
        url = ww.URL_GET_TIME_VAL
        stimestamp = timestamp.strftime("%d/%m/%Y %H:%M")
        params = {'tagnaam':tagname, 'timestamp':stimestamp}
        return self._get_request_result(url, params)

    def get_lims(self, mpoint, analysis,  start, end):
        """Wrapper on the get lims Wrapper

        INPUT
        mpoint   : monsterpunt code
        analysis : analysis code
        start    : start date (datetime)
        end      : end date (datetime)

        OUTPUT
        Pandas dataframe or None in case of error
        """
        url = ww.URL_GET_LIMS
        sstart = start.strftime("%d-%m-%Y")
        send = end.strftime("%d-%m-%Y")
        params = {'monsterpunt':mpoint, 'analyse':analysis, 'starttijd':sstart, 'eindtijd':send}
        return self._get_request_result(url, params)

    def print_log(self):
        """Prints the logbook as seperated lines"""
        for line in self._logbook:
            print(line)

# EXAMPLES
if __name__=="__main__":
    api = API()

    #get current value
    #df1 = api.get_curr_val("VVZ1GA01GM00__VD")

    #print(df1)

    #get trend
    #start = datetime.datetime(2015,1,1)
    #end = datetime.datetime(2015,12,31)
    #df2 = api.get_trend(tagname='2W325KM01TIT001', alist='GAS-DW-VD', start=start, end=end)
    #print df2

    #get trend pivot
    #start = datetime.datetime(2015,1,1)
    #end = datetime.datetime(2015,12,31)
    #df3 = api.get_trend_pivot(tagname='VVZ1GA01GM001_VD', alist='GAS-DW-VD', start=start, end=end)
    #print(df3)

    #testdate = datetime.datetime(2016,5,12,19,0)
    #print testdate
    #df4 = api.get_time_val("2W325KM01TIT001", testdate) #werkt nog niet goed!
    #print(df4)

    start = datetime.datetime(2005,7,1)
    end = datetime.datetime(2015,7,11)
    df5 = api.get_lims("PLD-RW-006", "MONTIJD", start, end)

    print(df5)

    api.print_log()
