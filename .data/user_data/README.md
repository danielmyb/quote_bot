# User data directory

This directory contains all data about all users that have started the bot. 

The data is stored inside json files that are named after the users telegram ID.

### Example structure:

```json
{
  "user_id": 123456789,
  "language": "DE",
  "daily_ping": true,
  "events": {
    "0": [],
    "1": [],
    "2": [],
    "3": [],
    "4": [],
    "5": [{
       "title": "Test",
       "content": "Testing Content",
       "event_type": 1,
       "event_time": "10:00"
      }],
    "6": []
  }
}
```

Inside these files the data of a user is saved.
This includes configuration values (like the language) and event data.