# Florida Poly Class Scraper
A scraper to get the data from Florida Polytechnic's CAMs system written in Python using MechanicalSoup

## Usage
From the console:
`python scrape.py`

## Configuration
To configure the scraper, add a text file to the directory called `config.txt`. Then, add the following to it:
```
username: ghutchison2600
password: 7up7upWhat'sUp?7up
semester: SP 2017
```
Replace the values with your username/password and your preferred semester.
(Note: Username/password information is necessary to access CAMs' class data, because it is only visible to Florida Polytechnic University students)

## Output
When finished, the data is saved in `output.json`

### Output Format:
```
"CourseID": [ // ID of containing course
    {
        "section": // the section number
        "seatsMax": // how many seats total the class can hold
        "seatsLeft": // how many seats are still open
        "meetings": [ // an individual meeting time
            {
                "room": // the room that the class meets in
                "campus": // the campus
                "building": // the building that the class meets in
                "professor": // the professor teaching the class
                "days": // the days when the class meets
                "time": { // the times during which the class is held
                    "start": {
                        "m": 30,
                        "h": 9
                    },
                    "end": {
                        "m": 45,
                        "h": 10
                    }
                }
            },
            ...
        ]
    },
    ...
```

### Output Example:
```json
"PSY2012GESS": [
    {
        "section": "01",
        "seatsMax": 30,
        "seatsLeft": 17,
        "meetings": [
            {
                "room": "1060",
                "campus": "",
                "building": "IST",
                "professor": "Howell, Ali",
                "days": "MW",
                "time": {
                    "start": {
                        "m": 30,
                        "h": 9
                    },
                    "end": {
                        "m": 45,
                        "h": 10
                    }
                }
            }
        ]
    }
]
```

## Dependencies
* [MechanicalSoup](https://www.github.com/hickford/MechanicalSoup)
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
* [lxml](http://lxml.de/)

([How to install python packages](https://packaging.python.org/installing/))
