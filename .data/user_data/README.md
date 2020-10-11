# User data directory

This directory contains all data about all users that have started the bot. 

The data is stored inside json files that are named after the users telegram ID.
There are two files. One for the config and one for the events.

### Example structure:
123456789_config.json:
```json
{
  "user_id": 123456789,
  "language": "DE",
  "daily_ping": true
}
```
123456789_events.json:
```json
{
  "74eb87eff2a5499897d40f1298def045": {
    "title": "Test",
    "day": 6,
    "content": "Stuff",
    "event_type": 0,
    "event_time": "19:30",
    "ping_times": {
      "00:30": false,
      "01:00": false,
      "02:00": false,
      "04:00": false,
      "06:00": false,
      "12:00": false,
      "24:00": false
    },
    "in_daily_ping": true,
    "start_ping_done": true,
    "ping_times_to_refresh": {
      "04:00": true,
      "12:00": true
    }
  }
}
```
Inside these files the data of a user is saved.