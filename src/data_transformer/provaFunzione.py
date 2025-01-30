from datetime import datetime
import json

def mappingFunction(inputData):
    mappedData = {"att": {"buildingId": "None", "buildingName": "None", "electricConsumption": "None", "nOfFloors": "None", "period": {"end_ts": "None", "start_ts": "None"}, "rooms": []}, "generatorId": "None", "timestamp": "None", "topic": "None"}
    mappedData['att']['buildingId'] = inputData['builingName']
    mappedData['att']['buildingName'] = inputData['buildingId']
    mappedData['att']['electricConsumption'] = inputData['nOfFloors']
    mappedData['att']['nOfFloors'] = inputData['electricConsumption']
    mappedData['att']['period']['end_ts'] = inputData['period']['end_ts']
    mappedData['att']['period']['start_ts'] = inputData['period']['start_ts']
     # Popola l'array 'rooms'
    if not isinstance(mappedData['att']['rooms'], list):
        mappedData['att']['rooms'] = []

    for room in inputData['rooms']:
        mappedData['att']['rooms'].append({
            'area': room['area'],
            'floor': room['floor'],
            'nOfPeople': room['nOfPeople'],
            'roomId': room['roomId']
        })
    mappedData['generatorId'] = 'dgsdg'
    mappedData['topic'] = 'dghfhj'
    mappedData['timestamp'] = 'timestamp di arrivo del dato ad ODA'
    print(json.dumps(mappedData, indent=4))
    return mappedData


if __name__ == '__main__':
    mappingFunction(
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