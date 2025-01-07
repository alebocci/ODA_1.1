import json

def mappingFunction(inputData):
    mappedData = {}
    mappedData['data'] = {}
    mappedData['data']['data'] = {'value': inputData['data'], 'unit': 'None'}
    mappedData['data']['buildingId'] = {'value': inputData['data']['buildingId'], 'unit': 'None'}
    mappedData['data']['buildingName'] = {'value': inputData['data']['buildingName'], 'unit': 'None'}
    mappedData['data']['electricConsumption'] = {'value': inputData['data']['electricConsumption'], 'unit': 'kwh'}
    mappedData['data']['nOfFloors'] = {'value': inputData['data']['nOfFloors'], 'unit': 'None'}
    mappedData['data']['period'] = {'value': inputData['data']['period'], 'unit': 'None'}
    mappedData['data']['end_ts'] = {'value': inputData['data']['period']['end_ts'], 'unit': 'None'}
    mappedData['data']['start_ts'] = {'value': inputData['data']['period']['start_ts'], 'unit': 'None'}
    mappedData['data']['rooms'] = {'value': inputData['data']['rooms'], 'unit': 'None'}
    mappedData['data']['area'] = {'value': inputData['data']['rooms'][0]['area'], 'unit': 'm^2'}
    mappedData['data']['floor'] = {'value': inputData['data']['rooms'][0]['floor'], 'unit': 'None'}
    mappedData['data']['nOfPeople'] = {'value': inputData['data']['rooms'][0]['nOfPeople'], 'unit': 'None'}
    mappedData['data']['roomId'] = {'value': inputData['data']['rooms'][0]['roomId'], 'unit': 'None'}
    mappedData['generator_id'] = inputData.get('generatorId')
    mappedData['timestamp'] = inputData.get('timestamp')
    mappedData['topic'] = inputData.get('topic')
    # stampo con indentazione
    print(json.dumps(mappedData, indent=4))
    return mappedData


if __name__ == '__main__':
    mappingFunction({
    "timestamp": "ora", 
    "generatorId": "generatore con oggetti", 
    "topic": "topic con Array", 
    "data": {
        "buildingId": "1234", 
        "nOfFloors": "5", 
        "buildingName": "edificio 1", 
        "rooms": [
            {
                "area": "32",
                "nOfPeople": "4",
                "floor": "2",
                "roomId": "1"
            }
        ],
        "electricConsumption": "234.78",
        "period": {
            "start_ts": "11:22:33",
            "end_ts": "22:33:44"
        }
    }
}
   
)
    

"""
 {
        "timestamp": "11:22:33", 
        "generatorId": "generatore chaive:valore", 
        "topic": "solo chiave:valore", 
        "buildingId": "1234", 
        "buildingName": "edificio t", 
        "area": "200",
        "electricConsumption": "567.89"
    }
"""