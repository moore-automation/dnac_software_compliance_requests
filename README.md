# Functionality

Pulls device and image data using below endpoints and creates a pie chart, csv file and outputs to terminal.

```bash
python collection.py
```

An env file is used to store DNAC hostname/IP and username/password. Replace the credentials within example.env and rename as .env before execution (example values are provided).

## Disclaimer

This code is very rudementary and intended for demonstration, it could be extended to include more verbose information and variety of graphs as requried.

## Requirements

- pandas
- python-dotenv
- requests

```bash
pip -r install requirements.txt
```
