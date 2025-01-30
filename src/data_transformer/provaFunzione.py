from datetime import datetime
import json

def mappingFunction(inputData):
    mappedData = {}
    mappedData['data'] = {}
    mappedData['data']['att'] = {
        'value': inputData['att'],
        'unit': 'None'
    }
    mappedData['data']['buildingId'] = {
        'value': inputData['att']['buildingId'],
        'unit': 'None'
    }
    mappedData['data']['buildingName'] = {
        'value': inputData['att']['buildingName'],
        'unit': 'None'
    }
    mappedData['data']['electricConsumption'] = {
        'value': inputData['att']['electricConsumption'],
        'unit': 'kWh'
    }
    mappedData['data']['nOfFloors'] = {
        'value': inputData['att']['nOfFloors'],
        'unit': 'None'
    }
    mappedData['data']['period'] = {
        'value': inputData['att']['period'],
        'unit': 'None'
    }
    mappedData['data']['end_ts'] = {
        'value': inputData['att']['period']['end_ts'],
        'unit': 'None'
    }
    mappedData['data']['start_ts'] = {
        'value': inputData['att']['period']['start_ts'],
        'unit': 'None'
    }
    mappedData['data']['rooms'] = {
        'value': inputData['att']['rooms'],
        'unit': 'None'
    }
    mappedData['data']['area'] = []
    for i, item in enumerate(inputData['att']['rooms']):
        mappedData['data']['area'].append({
            'value': item['area'],
            'unit': 'm^2'
        })
    mappedData['data']['floor'] = []
    for i, item in enumerate(inputData['att']['rooms']):
        mappedData['data']['floor'].append({
            'value': item['floor'],
            'unit': 'None'
        })
    mappedData['data']['nOfPeople'] = []
    for i, item in enumerate(inputData['att']['rooms']):
        mappedData['data']['nOfPeople'].append({
            'value': item['nOfPeople'],
            'unit': 'None'
        })
    mappedData['data']['roomId'] = []
    for i, item in enumerate(inputData['att']['rooms']):
        mappedData['data']['roomId'].append({
            'value': item['roomId'],
            'unit': 'None'
        })
    mappedData['generator_id'] = inputData.get('generatorId')
    mappedData['timestamp'] = inputData.get('timestamp')
    mappedData['topic'] = inputData.get('topic')
    print(json.dumps(mappedData, indent=4))
    return mappedData


if __name__ == '__main__':
    mappingFunction(
     {
    "timestamp": "ora", 
    "generatorId": "generatore con oggetti", 
    "topic": "topic con Array", 
    "att": {
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
    "buildingId": "9378",
    "nOfFloors": 8,
    "builingName": "Edificio T",
    "rooms": [
             {
                "area": 28,
                "nOfPeople": 5,
                "floor": 0,
                "roomId": 1
            },
            {
                "area": 30,
                "nOfPeople": 6,
                "floor": 0,
                "roomId": 2
            }
    ],
    "electricConsumption": 449.2,
    "period": {
        "start_ts": "2024-07-20T00:00",
        "end_ts": "2024-07-20T22:12"
    }
}

{
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