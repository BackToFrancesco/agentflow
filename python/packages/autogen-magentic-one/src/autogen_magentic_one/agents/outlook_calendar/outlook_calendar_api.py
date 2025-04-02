import sys
import requests
import os
from typing import List, Optional, Dict, Any
from datetime import datetime, time, timedelta
from dotenv import load_dotenv
import certifi
from ..utils.ms_graph import generate_access_token

#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Enable only for testing
#from utils.ms_graph import generate_access_token # Enable only for testing

class OutlookCalendarAPI:
    def __init__(self):
        load_dotenv()
        self.APPLICATION_ID = os.getenv('APPLICATION_ID')
        self.CLIENT_SECRET = os.getenv('CLIENT_SECRET')
        self.SCOPES = ['User.Read', 'Calendars.ReadWrite']
        self.base_url = 'https://graph.microsoft.com/v1.0/'

    def _get_access_token(self):
        if not self.APPLICATION_ID or not self.CLIENT_SECRET:
            raise ValueError("APPLICATION_ID or CLIENT_SECRET not set in environment variables")
        return generate_access_token(app_id=self.APPLICATION_ID, scopes=self.SCOPES)['access_token']

    def _get_headers(self):
        return {
            'Authorization': f'Bearer {self._get_access_token()}',
            'Content-Type': 'application/json'
        }

    def get_calendar_events(self, filter_params=None, limit=None) -> Dict[str, Any]:
        url = f'{self.base_url}me/events'
        if filter_params:
            url += f'?$filter={filter_params}'
        
        try:
            all_events = []
            while url:
                response = requests.get(url, headers=self._get_headers(), verify=certifi.where())
                response.raise_for_status()
                data = response.json()
                events = data.get('value', [])
                
                event_details = [
                    {
                        'id': event.get('id'),
                        'subject': event.get('subject'),
                        'start': event.get('start'),
                        'end': event.get('end'),
                        'organizer': event.get('organizer'),
                        'attendees': event.get('attendees')
                    }
                    for event in events
                ]
                
                all_events.extend(event_details)
                
                if limit and len(all_events) >= limit:
                    return {"events": all_events[:limit]}
                
                url = data.get('@odata.nextLink')
            
            return {"events": all_events}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def create_meeting(self, subject: str, start_time: str, end_time: str, 
                       attendees: Optional[List[str]] = None, 
                       location: Optional[str] = None, 
                       body: Optional[str] = None) -> dict:
        """
        Create a new meeting in the Outlook calendar.

        :param subject: The subject of the meeting
        :param start_time: The start time of the meeting (in ISO 8601 format)
        :param end_time: The end time of the meeting (in ISO 8601 format)
        :param attendees: Optional list of attendee email addresses
        :param location: Optional location of the meeting
        :param body: Optional body content of the meeting invitation
        :return: A dictionary containing the created event details or error information
        """
        url = f'{self.base_url}me/events'
        
        event = {
            "subject": subject,
            "start": {
                "dateTime": start_time,
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "UTC"
            },
        }

        if attendees:
            event["attendees"] = [{"emailAddress": {"address": email}} for email in attendees]
        
        if location:
            event["location"] = {"displayName": location}
        
        if body:
            event["body"] = {
                "contentType": 'HTML',
                "content": body
            }

        try:
            response = requests.post(url, headers=self._get_headers(), json=event, verify=certifi.where())
            response.raise_for_status()
            result = response.json()
            return {
                "id": result.get("id"),
                "subject": result.get("subject"),
                "start": result.get("start"),
                "end": result.get("end"),
                "attendees": [attendee.get("emailAddress", {}).get("address") for attendee in result.get("attendees", [])],
                "location": result.get("location", {}).get("displayName"),
                "webLink": result.get("webLink")
            }
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_available_slots(self, 
                            start_time: str,
                            end_time: str,
                            meeting_duration: int = 60, 
                            buffer: int = 0,
                            lunch_hour: tuple = (13, 14)) -> Dict[str, Any]:
        """
        Find available slots for meetings within a specified time range for a single day.

        :param start_time: The start of the time range (ISO 8601 format)
        :param end_time: The end of the time range (ISO 8601 format)
        :param meeting_duration: Duration of the meeting in minutes (default 60)
        :param buffer: Buffer time between meetings in minutes (default 0)
        :param lunch_hour: Tuple of (start_hour, end_hour) for lunch break (default (13, 14) for 1 PM to 2 PM)
        :return: Dictionary with either available slots or an error message
        """
        range_start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        range_end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))

        if range_start.date() != range_end.date():
            return {"error": "Start and end times must be on the same day."}

        available_slots = []
        
        # Get events for the day
        events_result = self.get_calendar_events(
            filter_params=f"start/dateTime ge '{range_start.isoformat()}' and end/dateTime le '{range_end.isoformat()}'"
        )

        if "error" in events_result:
            return {"error": f"Error retrieving calendar events: {events_result['error']}"}

        events = events_result.get("events", [])
        events.sort(key=lambda x: x['start']['dateTime'])

        current_time = range_start

        def add_slot(start, end):
            while start < end:
                if start.hour == lunch_hour[0]:
                    start = start.replace(hour=lunch_hour[1], minute=0)
                    if start >= end:
                        break
                slot_end = min(end, start + timedelta(minutes=meeting_duration))
                if (slot_end - start).total_seconds() / 60 >= meeting_duration:
                    available_slots.append({
                        "start": start.isoformat(),
                        "end": slot_end.isoformat()
                    })
                start = slot_end

        if not events:
            add_slot(range_start, range_end)
        else:
            for event in events:
                event_start = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                event_end = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
                
                if current_time < event_start:
                    add_slot(current_time, event_start)
                
                current_time = max(current_time, event_end + timedelta(minutes=buffer))

            # Check for available slots after the last event
            if current_time < range_end:
                add_slot(current_time, range_end)

        return {"available_slots": available_slots}

# if __name__ == "__main__":
#     api = OutlookCalendarAPI()
#     events = api.get_calendar_events(limit=10)
#     print(f"Retrieved {len(events['events'])} events:")
#     for event in events['events']:
#         print(f"Subject: {event['subject']}")
#         print(f"Start: {event['start']['dateTime']}")
#         print(f"End: {event['end']['dateTime']}")
#         print("---")
#     # new_meeting = api.create_meeting(                                                                                                                                 
#     #     subject="Team Meeting",                                                                                                                                       
#     #     start_time="2023-06-01T10:00:00",                                                                                                                             
#     #     end_time="2023-06-01T11:00:00",                                                                                                                               
#     #     attendees=["colleague1@example.com", "colleague2@example.com"],                                                                                               
#     #     location="Conference Room A",                                                                                                                                 
#     #     body="Let's discuss our project progress."                                                                                                                                      
#     # )
#     # print(new_meeting)
#     # call get_available_slots
#     slots = api.get_available_slots(
#         start_time="2023-06-01T08:00:00",
#         end_time="2023-06-02T17:00:00", 
#         meeting_duration=60,
#         buffer=15,
#         lunch_hour=(13, 14)
#     )
#     print("\nAvailable meeting slots:")
#     print(slots)
#     for slot in slots.get("available_slots", []):
#         start_time = datetime.fromisoformat(slot['start']).strftime("%B %d, %Y at %I:%M %p")
#         end_time = datetime.fromisoformat(slot['end']).strftime("%I:%M %p")
#         print(f"- {start_time} to {end_time}")
