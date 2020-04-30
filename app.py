from flask import Flask
from flask_restful import Api,request
from flask_cors import CORS
import json
import requests
import datetime

app = Flask(__name__)
api = Api(app)
CORS(app)
global lastresponse

@app.route('/process_data', methods=['POST'])
def post():
    requestbody=request.json
    global lastresponse
    lastresponse=requestbody
    updateairtable(requestbody)
    return "Success",201

@app.route('/getwritebackdata')
def get():
    global lastresponse
    return lastresponse,200

def updateairtable(changes):
    airtable_key='<YOUR_AIRTABLE_KEY>'
    airtable_get_records_url='<YOUR_AIRTABLE_URL>'
    airtable_patch_url='https://api.airtable.com/v0/appzQXCHIDNUJ6RNL/Imported%20table/'
    recordlist=requests.get(airtable_get_records_url,headers={
                                        'Authorization': 'Bearer '+airtable_key},
                                    verify=False)
    recordjsonarray=recordlist.json()['records']
    list_of_changes=changes['changedDataArray']
    for change in list_of_changes.keys():
        task=change.split("~!~")[0]
        subtask = change.split("~!~")[1]
        for record in recordjsonarray:
            if(record['fields']['Task']==task and record['fields']['Sub Task']==subtask):
                patchdata = {}
                record['fields']['ActualStart']=get_date_string_from_time_stamp(list_of_changes[change]['actualStart'])
                record['fields']['ActualEnd'] = get_date_string_from_time_stamp(list_of_changes[change]['actualEnd'])
                record['fields']['PlannedStart'] = get_date_string_from_time_stamp(list_of_changes[change]['baselineStart'])
                record['fields']['PlannedEnd'] = get_date_string_from_time_stamp(list_of_changes[change]['baselineEnd'])
                patchdata['fields']=record['fields']
                requests.patch(airtable_patch_url+record['id'],headers={
                                        'Authorization': 'Bearer '+airtable_key,'Content-Type': 'application/json'},data=json.dumps(patchdata),
                                    verify=False)

def get_date_string_from_time_stamp(timestamp):
    date_time = datetime.datetime.fromtimestamp(timestamp/1000)
    d=date_time.strftime("%m-%d-%Y")
    return d

if __name__ == '__main__':
    app.run(debug=True)
