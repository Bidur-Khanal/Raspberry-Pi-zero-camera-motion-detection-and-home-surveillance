import json

class configuration:
    def __init__(self):
        self.a=0

    def read_data(self):
        with open("Data/configuration.json", "r") as jsonFile:
             data = json.load(jsonFile)
        return data
        
    def write_data(self,data):
        threshold =data["Devices_Settings"]["Camera"][0]["Current_Sensitivity"]
        print threshold

call = configuration()
data= call.read_data()
call.write_data(data)
        
                
        
