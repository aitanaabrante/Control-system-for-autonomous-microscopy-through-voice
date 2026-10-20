# the LasxApi files are expected to be in a subfolder 'LasxApi' next to this file.
import sys
from LasxApi import PYLICamApiConnector as lasxApi

#Start
print("Python exe:", sys.executable) #Report on Python env

#LasX-API
clientName = "PythonClient"       #Defines where the Settings file is searched for.
client = lasxApi.LasxApiClientPyModel
 
#connect
def connect():
    confirmed = client.Connect(clientName)
    print(f"Connected:[{"OK" if confirmed else "Timeout"}]")
    return  confirmed