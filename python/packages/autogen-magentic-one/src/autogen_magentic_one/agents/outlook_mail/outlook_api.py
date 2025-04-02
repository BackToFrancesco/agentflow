import sys
import requests
import os
from dotenv import load_dotenv
import certifi
from ..utils.ms_graph import generate_access_token

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Enable only for testing
# from utils.ms_graph import generate_access_token # Enable only for testing

class OutlookAPI:
    def __init__(self):
        load_dotenv()
        self.APPLICATION_ID = os.getenv('APPLICATION_ID')
        self.CLIENT_SECRET = os.getenv('CLIENT_SECRET')
        self.SCOPES = ['User.Read', 'Mail.Read', 'Mail.ReadWrite', 'Mail.Send']
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

    def get_all_emails(self, filter_params=None, limit=None):
        url = f'{self.base_url}me/messages'
        if filter_params:
            url += f'?$filter={filter_params}'
        
        try:
            all_emails = []
            while url:
                response = requests.get(url, headers=self._get_headers(), verify=certifi.where())
                response.raise_for_status()
                data = response.json()
                emails = data.get('value', [])            
                id_sender_recipients_subject_body = [
                    {
                        'id': x.get('id'),
                        'sender': x.get('sender'),
                        'toRecipients': x.get('toRecipients'),
                        'subject': x.get('subject'), 
                        'bodyPreview': x.get('bodyPreview')
                    } 
                    for x in emails
                ]            
                all_emails.extend(id_sender_recipients_subject_body)
                
                if limit and len(all_emails) >= limit:
                    return {"emails": all_emails[:limit]}
                
                url = data.get('@odata.nextLink')
            
            return {"emails": all_emails}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_unread_emails(self):
        return self.get_all_emails(filter_params='isRead eq false')

    def move_email_to_folder(self, email_id, folder_id):
        url = f'{self.base_url}me/messages/{email_id}/move'
        data = {'destinationId': folder_id}
        response = requests.post(url, headers=self._get_headers(), json=data).json()
        if "error" in response:
            return response
        else:
            return {"success": True}

    def get_email_folders(self):
        url = f'{self.base_url}me/mailFolders'
        try:
            response = requests.get(url, headers=self._get_headers(), verify=certifi.where())
            response.raise_for_status()
            folders = response.json().get('value', [])
            folder_info = [{"id": folder.get("id"), "displayName": folder.get("displayName")} for folder in folders]
            return {"folders": folder_info}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def create_email_folder(self, folder_name):
        url = f'{self.base_url}me/mailFolders'
        data = {'displayName': folder_name}
        response = requests.post(url, headers=self._get_headers(), json=data).json()
        if "error" in response:
            return response
        else:
            return {"success": True, "folder_id": response.get("id")}

    def get_email_by_id(self, email_id):
        url = f'{self.base_url}me/messages/{email_id}'
        response = requests.get(url, headers=self._get_headers())
        return response.json()

    def search_emails(self, query):
        url = f'{self.base_url}me/messages?$search="{query}"'
        response = requests.get(url, headers=self._get_headers(), verify=certifi.where())
        return response.json().get('value', [])

    def send_email(self, subject, body, to_recipients):
        recipients_str = ", ".join(to_recipients)

        print(f"Email Details:\nTo: {recipients_str}\nSubject: {subject}\nBody: {body}")
        if input("Do you want to send this email? (y/n): ").lower() != "y":
            return {"result": "rejected", "message": "Mail not sent because the user decided not to send it."}

        url = f'{self.base_url}me/messages'
        email_data = {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body
            },
            "toRecipients": [{"emailAddress": {"address": recipient}} for recipient in to_recipients]
        }

        try:
            # First, create a draft message
            create_response = requests.post(url, headers=self._get_headers(), json=email_data)
            create_response.raise_for_status()
            message_data = create_response.json()
            message_id = message_data.get('id')

            if not message_id:
                return {"result": "error", "message": "Failed to create draft message: No message ID returned"}

            # Then, send the draft message
            send_url = f'{self.base_url}me/messages/{message_id}/send'
            send_response = requests.post(send_url, headers=self._get_headers())
            send_response.raise_for_status()

            return {"result": "success", "message_id": message_id}
        except requests.exceptions.RequestException as e:
            return {"result": "error", "message": f"Failed to send email: {str(e)}"}

    def reply_to_mail(self, message_id, comment=None):
        # First, get the original email details
        original_email = self.get_email_by_id(message_id)
        subject = original_email.get('subject', '')
        sender = original_email.get('sender', {}).get('emailAddress', {}).get('address', 'Unknown')

        print(f"Reply Details:\nTo: {sender}\nSubject: RE: {subject}\nComment: {comment}")
        if input("Do you want to send this reply? (y/n): ").lower() != "y":
            return {"result": "rejected", "message": "Reply not sent because the user decided not to send it."}

        url = f'{self.base_url}me/messages/{message_id}/reply'
        
        reply_data = {}
        if comment:
            reply_data['comment'] = comment

        try:
            response = requests.post(url, headers=self._get_headers(), json=reply_data)
            response.raise_for_status()
            if response.status_code == 202:
                return {"result": "success", "message_id": message_id}
            else:
                return {"result": "error", "message": f"Failed to send reply with status code {response.status_code}."}
        except requests.exceptions.RequestException as e:
            return {"result": "error", "message": f"Failed to send reply: {str(e)}"}

# if __name__ == "__main__":                                                                                                                                                                       
#     api = OutlookAPI()

