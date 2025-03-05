import json
def mappingFunction(inputData):
    mappedData = {}
    if isinstance(inputData.get('data'), str):
        inputData['data'] = json.loads(inputData['data'])
    mappedData['data'] = {}
    mappedData['data']['data'] = {
        'value': inputData['data'],
        'unit': 'None'
    }
    mappedData['data']['building'] = {
        'value': inputData['data']['building'],
        'unit': 'None'
    }
    mappedData['data']['buildingId'] = {
        'value': inputData['data']['building']['buildingId'],
        'unit': 'None'
    }
    mappedData['data']['builingName'] = {
        'value': inputData['data']['building']['builingName'],
        'unit': 'None'
    }
    mappedData['data']['nOfFloors'] = {
        'value': inputData['data']['building']['nOfFloors'],
        'unit': 'None'
    }
    mappedData['data']['rooms'] = {
        'value': inputData['data']['building']['rooms'],
        'unit': 'None'
    }
    
    mappedData['data']['electricConsumption'] = {
        'value': inputData['data']['electricConsumption'],
        'unit': 'kWh'
    }
    mappedData['data']['period'] = {
        'value': inputData['data']['period'],
        'unit': 'None'
    }
    mappedData['data']['end_ts'] = {
        'value': inputData['data']['period']['end_ts'],
        'unit': 'None'
    }
    mappedData['data']['start_ts'] = {
        'value': inputData['data']['period']['start_ts'],
        'unit': 'None'
    }
    mappedData['generator_id'] = inputData.get('generator_id')
    mappedData['timestamp'] = inputData.get('timestamp')
    mappedData['topic'] = inputData.get('topic')
    print(json.dumps(mappedData, indent=4))
    return mappedData


if __name__ == '__main__':
    mappingFunction(
    {
        "data": "{\r\n  \"building\": {\r\n    \"buildingId\": \"7631\",\r\n    \"nOfFloors\": 4,\r\n    \"builingName\": \"Edificio O\",\r\n    \"rooms\": [\r\n      [\r\n        {\r\n          \"area\": 39,\r\n          \"nOfPeople\": 4,\r\n          \"floor\": 0,\r\n          \"roomId\": 1\r\n        }\r\n      ],\r\n      [\r\n        {\r\n          \"area\": 25,\r\n          \"nOfPeople\": 2,\r\n          \"floor\": 1,\r\n          \"roomId\": 1\r\n        },\r\n        {\r\n          \"area\": 48,\r\n          \"nOfPeople\": 4,\r\n          \"floor\": 1,\r\n          \"roomId\": 2\r\n        },\r\n        {\r\n          \"area\": 46,\r\n          \"nOfPeople\": 1,\r\n          \"floor\": 1,\r\n          \"roomId\": 3\r\n        },\r\n        {\r\n          \"area\": 30,\r\n          \"nOfPeople\": 1,\r\n          \"floor\": 1,\r\n          \"roomId\": 4\r\n        },\r\n        {\r\n          \"area\": 41,\r\n          \"nOfPeople\": 7,\r\n          \"floor\": 1,\r\n          \"roomId\": 5\r\n        },\r\n        {\r\n          \"area\": 37,\r\n          \"nOfPeople\": 1,\r\n          \"floor\": 1,\r\n          \"roomId\": 6\r\n        }\r\n      ],\r\n      [\r\n        {\r\n          \"area\": 26,\r\n          \"nOfPeople\": 7,\r\n          \"floor\": 2,\r\n          \"roomId\": 1\r\n        },\r\n        {\r\n          \"area\": 30,\r\n          \"nOfPeople\": 5,\r\n          \"floor\": 2,\r\n          \"roomId\": 2\r\n        },\r\n        {\r\n          \"area\": 47,\r\n          \"nOfPeople\": 2,\r\n          \"floor\": 2,\r\n          \"roomId\": 3\r\n        }\r\n      ],\r\n      [\r\n        {\r\n          \"area\": 30,\r\n          \"nOfPeople\": 5,\r\n          \"floor\": 3,\r\n          \"roomId\": 1\r\n        }\r\n      ]\r\n    ]\r\n  },\r\n  \"electricConsumption\": 137.4,\r\n  \"period\": {\r\n    \"start_ts\": \"2024-05-18T00:00\",\r\n    \"end_ts\": \"2024-05-18T04:48\"\r\n  }\r\n}",
        "generator_id": "Generator 0",
        "timestamp": "2024-12-23T15:57:45.000Z",
        "topic": "BuildingEnergyUsage"
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
