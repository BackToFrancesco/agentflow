import os
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import certifi

class JiraAPI:
    def __init__(self):
        load_dotenv()
        self.JIRA_DOMAIN = os.getenv('JIRA_DOMAIN')
        self.EMAIL = os.getenv('JIRA_EMAIL')
        self.API_TOKEN = os.getenv('JIRA_API_TOKEN')
        self.base_url = f'https://{self.JIRA_DOMAIN}.atlassian.net/rest/api/3/'

    def _get_headers(self):
        return {
            'Authorization': f'Basic {self._get_base64_credentials()}',
            'Content-Type': 'application/json'
        }

    def _get_base64_credentials(self):
        import base64
        credentials = f"{self.EMAIL}:{self.API_TOKEN}"
        return base64.b64encode(credentials.encode()).decode()

    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """
        Retrieve an issue by its key.

        :param issue_key: The key of the issue to retrieve
        :return: A dictionary containing the issue details or error information
        """
        url = f'{self.base_url}'
        
        try:
            response = requests.get(url, headers=self._get_headers(), verify=certifi.where())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(response.text)}

    def create_issue(self, project_key: str, issue_type: str, summary: str, description: str) -> Dict[str, Any]:
        """
        Create a new issue in Jira.

        :param project_key: The key of the project where the issue will be created
        :param issue_type: The type of the issue (e.g., "Bug", "Task", "Story")
        :param summary: The summary (title) of the issue
        :param description: The description of the issue
        :return: A dictionary containing the created issue details or error information
        """
        url = f'{self.base_url}issue'
        
        data = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "summary": summary,
                "issuetype": {
                    "name": issue_type
                },
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": description
                                }
                            ]
                        }
                    ]
                }
            }
        }

        print(f"Creating issue:\nProject (Key/ID): {project_key}\nIssue Type: {issue_type}\nSummary: {summary}\nDescription: {description}")
        # if input("Do you want to create this issue? (y/n): ").lower() != "y":
        #     return {"result": "rejected", "message": "Issue not created because the user decided not to create it."}

        try:
            response = requests.post(url, headers=self._get_headers(), json=data)
            response.raise_for_status()
            json_response = response.json()
            return {
                "id" : json_response["id"],
                "key" : json_response["key"],
                "name" : summary
            }
        except requests.exceptions.RequestException as e:
            return {"error": str(response.text)}

    def search_issues(self, jql: str, max_results: int = 50) -> Dict[str, Any]:
        """
        Search for issues using JQL (Jira Query Language).

        :param jql: The JQL query string
        :param max_results: The maximum number of results to return (default: 50)
        :return: A dictionary containing the search results or error information
        """
        url = f'{self.base_url}search'
        
        params = {
            "jql": jql,
            "maxResults": max_results
        }

        try:
            response = requests.get(url, headers=self._get_headers(), params=params, verify=certifi.where())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(response.text)}

    def get_all_issues(self, max_results: int = 1000) -> List[Dict[str, Any]]:
        """
        Retrieve all issues with extracted information.

        :param max_results: The maximum number of results to return (default: 1000)
        :return: A list of dictionaries containing extracted issue information
        """
        jql = "order by created DESC"
        return self._extract_issue_info(jql, max_results)

    def get_project_issues(self, project_name: str, max_results: int = 1000) -> List[Dict[str, Any]]:
        """
        Retrieve all issues for a specific project with extracted information.

        :param project_name: The name of the project to retrieve issues from
        :param max_results: The maximum number of results to return (default: 1000)
        :return: A list of dictionaries containing extracted issue information
        """
        jql = f"project = '{project_name}' order by created DESC"
        return self._extract_issue_info(jql, max_results)

    def _extract_issue_info(self, jql: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Helper method to extract issue information based on JQL query.

        :param jql: The JQL query string
        :param max_results: The maximum number of results to return
        :return: A list of dictionaries containing extracted issue information
        """
        data = self.search_issues(jql, max_results)
        
        if "error" in data:
            return [{"error": data["error"]}]

        extracted_info = []
        for issue in data.get("issues", []):
            fields = issue["fields"]
            extracted_info.append({
                "Key": issue["key"],
                "Summary": fields["summary"],
                "Project": fields["project"]["name"],
                "Issue Type": fields["issuetype"]["name"],
                "Priority": fields["priority"]["name"],
                "Status": fields["status"]["name"],
                "Created": fields["created"],
                "Updated": fields["updated"],
                "Due Date": fields.get("duedate", "None")
            })
        
        return extracted_info

    def get_all_projects(self):
        """
        Get a list of projects from the Slack API.

        Returns:
        list: A list of dictionaries containing project information.
        """
        url = f'{self.base_url}project'

        try:
            response = requests.get(url, headers=self._get_headers(), verify=certifi.where())
            response.raise_for_status()
            response_json = response.json()
            if isinstance(response_json, list):
                return [{
                    "name": project["name"],
                    "key": project["key"],
                    "id": project["id"],
                } for project in response_json]
        except requests.exceptions.RequestException as e:
            return {"error": str(response.text)}

# Example usage:
if __name__ == "__main__":
    jira = JiraAPI()
    
    # Get all issues
    # all_issues = jira.get_all_issues()
    # print("All issues:")
    # for issue in all_issues:
    #     print(issue)
    
    # Get issues for a specific project
    # project_issues = jira.get_project_issues("POC project")
    # print("\nIssues for project PROJ:")
    # for issue in project_issues:
    #     print(issue)
    
    # Get an issue
    # issue = jira.get_issue("PROJ-123")
    # print(issue)
    
#     # Create an issue
    # new_issue = jira.create_issue("SCRUM", "Task", "New task summary", "This is a description of the new task.")
    # print(new_issue)

    print(jira.get_projects())
#     
#     # Search for issues
#     search_results = jira.search_issues("project = PROJ AND status = Open")
#     print(search_results)
