import json
import re
import requests

from config import Config


class EmailService:
    def __init__(self) -> None:
        assistant_local, _, assistant_domain = self.extract_email_parts(Config.ASSISTANT_EMAIL)
        self.assistant_local = assistant_local
        self.assistant_domain = assistant_domain
        self.blacklist = list(map(lambda x: x.strip(), Config.EMAIL_BLACKLIST.strip().split(",")))
        self.respond_url = Config.RESPOND_EMAIL_WEBHOOK_URL
        self.send_url = Config.SEND_EMAIL_WEBHOOK_URL
        self.whitelist = list(map(lambda x: x.strip(), Config.EMAIL_WHITELIST.strip().split(",")))
        if assistant_local:
            self.blacklist.append(assistant_local) # Do not answer to itself

    def contains_blacklist_term(self, address: str) -> bool:
        for value in self.blacklist:
            if value and value in address:
                return True
        return False
    
    def contains_whitelist_term(self, address: str) -> bool:
        for value in self.whitelist:
            if value and value in address:
                return True
        return False
    
    @classmethod
    def extract_email_parts(cls, email: str) -> tuple[str, str | None, str]:
        """
        Extracts the local part, plus suffix (if any), and domain from an email address.

        Args:
            email (str): The email address to extract parts from.

        Returns:S
            tuple: (local_part, plus_suffix, domain)
        """
        match = re.match(r"([^+@]+)(?:\+([^@]+))?@(.+)", email.strip())
        if match:
            local_part = match.group(1) # Everything before the '+' or '@'
            plus_suffix = match.group(2) # Everything after the '+' but before '@', if present
            domain = match.group(3) # Everything after '@'
            return local_part, plus_suffix, domain
        else:
            raise ValueError("Invalid email format")
    
    @classmethod
    def normalize_email(cls, email: str) -> str:
        """
        Normalizes an email address by removing the '+' suffix and its appended content.
        """
        local_part, domain = email.strip().split("@")
        local_part = re.sub(r"\+.*", "", local_part)
        return f"{local_part}@{domain}"
    
    def respond(self, thread_id: str, message_id: str, message: str) -> None:
        if len(self.respond_url) == "":
            raise ValueError("RESPOND_EMAIL_WEBHOOK_URL env variable not set")
        headers = {
            "Content-Type": "application/json",
        }
        try:
            response = requests.post(self.respond_url, data=json.dumps({
                "thread_id": thread_id,
                "message_id": message_id,
                "message": message,
            }), headers=headers)
            if response.status_code != 200:
                raise ValueError(f"Failed to respond. Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            raise ValueError(f"An error occurred: {e}")

    def send(self, subject: str, message: str, to_list: list[str]) -> None:
        if len(self.send_url) == "":
            raise ValueError("SEND_EMAIL_WEBHOOK_URL env variable not set")
        headers = {
            "Content-Type": "application/json",
        }
        try:
            response = requests.post(self.send_url, data=json.dumps({
                "subject": subject,
                "message": message,
                "to_email": ",".join(to_list),
            }), headers=headers)
            if response.status_code != 200:
                raise ValueError(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            raise ValueError(f"An error occurred: {e}")
