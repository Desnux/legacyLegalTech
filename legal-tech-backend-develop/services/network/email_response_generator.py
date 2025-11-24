import logging
import tempfile

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field
from sqlmodel import select

from database.ext_db import Session
from models.pydantic import (
    AttachmentInformation,
    AttachmentInformationExtended,
    LegalResolution,
)
from models.sql import Case, CaseParty
from providers.openai import get_structured_generator
from services.extractor import LegalResolutionExtractor
from services.loader import PdfLoader
from services.tracker import CaseTracker
from services.v2.document.demand_exception import DemandExceptionEventManager
from services.v2.document.dispatch_resolution import DispatchResolutionEventManager
from storage import S3Storage


FRONTEND_CASE_URL_PREFIX = "http://gpt-strategist.us-east-1.elasticbeanstalk.com:3002/case/"


class EmailType(str, Enum):
    SPAM = "spam"
    GREETING = "greeting"
    ABOUT_YOU = "about_you"
    DISPATCH_RESOLUTION = "dispatch_resolution"
    EXCEPTIONS = "exceptions"
    RESOLUTION = "resolution"
    GENERIC_UPDATE = "generic_update"


class EmailRequest(BaseModel):
    case_uuid: UUID | str | None = Field(None, description="UUID related to a legal case inside the message, may be None if not provided")
    email_type: EmailType | str | None = Field(None, description="Type of the email based on its intention")
    from_party: CaseParty | str | None = Field(None, description="Legal party that send the email")
    to_party: CaseParty | str | None = Field(None, description="Legal party that should respond to the email")
    title: str | None = Field(None, description="Title used to label the email inside a chain of events or updates related to a legal case")
    summary: str | None = Field(None, description="Summary used to describe the email event inside a chain of events or updates related to a legal case")


class EmailResponse(BaseModel):
    message: str | None = Field(None, description="Text content of the response")


class EmailResponseGenerator:
    def __init__(self, session: Session, thread_id: str, message_id: str, from_email: str, to_list: list[str], case_id: UUID | None = None) -> None:
        self.attachments: list[str] = []
        self.case_uuid = case_id
        self.from_email = from_email
        self.to_list = to_list
        self.message_id = message_id
        self.session = session
        self.thread_id = thread_id
        try:
            self.storage = S3Storage()
        except Exception as e:
            logging.warning(f"Could not connect to S3: {e}")
            self.storage = None

        if self.storage:
            for i in range(8):
                key = f"email_messages/{self.thread_id}/{self.message_id}/attachment_{i}.pdf"
                if self.storage.exists(key):
                    self.attachments.append(key)
                else:
                    break
    
    def generate_response(self, message: str) -> str | None:
        information_list: list[AttachmentInformationExtended] = []
        if self.storage:
            for key in self.attachments:
                try:
                    information, content = self._extract_attachment_information(key)
                    information_extended = AttachmentInformationExtended(**information.model_dump(), key=key, content=content)
                    information_list.append(information_extended)
                except Exception as e:
                    logging.warning(f"Error while processing email attachment: {e}")
        
        request_prompt = self._get_request_prompt(message, information_list)
        request_llm: EmailRequest = get_structured_generator(EmailRequest).invoke(request_prompt)
        if request_llm.case_uuid and self.case_uuid is None:
            try:
                self.case_uuid = UUID(request_llm.case_uuid)
            except ValueError:
                logging.warning(f"Invalid case UUID ({request_llm.case_uuid})")
        match request_llm.email_type:
            case EmailType.SPAM:
                logging.info("Spam detected, ignored")
                return None
        
        errors: list[str] = []
        info: list[str] = []
        legal_case: Case | None = None
        if self.case_uuid:
            try:
                statement = select(Case).where(Case.id == self.case_uuid)
                legal_case = self.session.exec(statement).first()
                if not legal_case:
                    errors.append(f"The case {self.case_uuid} does not exist in the database, system cannot provide assistence")
            except Exception as e:
                logging.warning(f"Could not get case: {e}")    
                errors.append("System could not retrieve the related legal case from the database")
        else:
            errors.append("The email does not contain or mention a relevant legal case UUID, system cannot provide assistence without it")
        
        if legal_case and information_list:
            case_tracker = CaseTracker(legal_case)

            if request_llm.email_type == EmailType.DISPATCH_RESOLUTION:
                try:
                    event_manager = DispatchResolutionEventManager(legal_case)
                    information, event = event_manager.create_from_attachments(self.session, information_list)
                    try:
                        suggestions = event_manager.create_suggestions(self.session, event, information)
                        if suggestions is None:
                            errors.append(f"System could not generate suggestions for disparch resolution from email")
                        elif len(suggestions) == 0:
                            info.append("Indicate that everything is in order and the user should wait for futher developments")
                        else:
                            info.append(f"Communicate the following suggestions as possible responses to the dispatch resolution sent by the court: <suggestions>{[s.model_dump_json() for s in suggestions]}</suggestions>")
                    except Exception as e:
                        logging.warning(f"Could not generate smart suggestions for dispatch resolution from email: {e}")
                        info.append("Provide valid response suggestions to the dispatch resolution if there were any indications or requests, otherwise just indicate that everything is in order and the user should wait for futher developments")
                        info.append(f"Consider: <resolution>{information.resolution}</resolution>")
                except Exception as e:
                    logging.warning(f"Could not process dispatch resolution from email: {e}")
                    errors.append(f"System could not process dispatch resolution from email: {e}")
            
            elif request_llm.email_type == EmailType.EXCEPTIONS:
                try:
                    event_manager = DemandExceptionEventManager(legal_case)
                    information, event = event_manager.create_from_attachments(self.session, information_list)
                    try:
                        suggestions = event_manager.create_suggestions(self.session, event, information)
                        if suggestions is None:
                            errors.append(f"System could not generate suggestions for exceptions raised by the defendants from email")
                        elif len(suggestions) == 0:
                            info.append("Indicate that there is no need to respond and the user should wait for futher developments")
                        else:
                            info.append(f"Communicate the following suggestions as possible responses to the exceptions raised by the defendants: <suggestions>{[s.model_dump_json() for s in suggestions]}</suggestions>")
                    except Exception as e:
                        logging.warning(f"Could not generate smart suggestions for exceptions raised by the defendants from email: {e}")
                        info.append("Provide valid response suggestions to the exceptions raised by the defendants")
                        info.append(f"Consider: <exceptions>{[e.model_dump() for e in information.exceptions or []]}</exceptions>")
                except Exception as e:
                    logging.warning(f"Could not process exceptions from email: {e}")
                    errors.append(f"System could not exceptions from email: {e}")
            
            elif request_llm.email_type == EmailType.RESOLUTION:
                try:
                    legal_resolution_structure: LegalResolution | None = case_tracker.create_legal_resolution_from_attachments(self.session, information_list)
                    if legal_resolution_structure is None:
                        errors.append("System could not store the legal resolution in our database, please contact the administrator about it")
                    else:
                        info.append(f"Consider: <resolution>{legal_resolution_structure.resolution}</resolution>")
                        hearing_info = None
                        if legal_resolution_structure.resolution:
                            hearing_info = LegalResolutionExtractor().extract_hearing_information(legal_resolution_structure.resolution)
                        if hearing_info:
                            info.append(f"Indicate that there will be a probatory period with a hearing set at {hearing_info.hearing_hour} during the days {hearing_info.hearing_days} (relative to the probatory period, for example -1 is the last day and 3 is the third day).")
                        else:
                            info.append("Indicate that everything is in order and the user should wait for futher developments")
                except Exception as e:
                    logging.warning(f"Could not process legal resolution from email: {e}")
                    errors.append(f"System could not process legal resolution from email: {e}")
            
            else:
                errors.append("The email is not about a court resolution or exceptions raise by defendants, system cannot provide assistance")
        else:
            errors.append("The email does not contain relevant attachments, system cannot provide assistence without them")
        
        response_prompt = self._get_response_prompt(message, request_llm.model_dump_json(exclude={"case_uuid", "email_type"}), info, errors)
        response_llm: EmailResponse = get_structured_generator(EmailResponse).invoke(response_prompt)
        return response_llm.message
    
    def _extract_attachment_information(self, key: str) -> tuple[AttachmentInformation, str]:
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            self.storage.download(key, temp_file.name)
            temp_file.flush()
            temp_file.seek(0)
            loader = PdfLoader(temp_file.name)
            documents = loader.load()
            content = "\n\n".join([document.page_content for document in documents])
            information_prompt = self._get_attachment_prompt(content)
            information: AttachmentInformation = get_structured_generator(AttachmentInformation).invoke(information_prompt)
            return information, content

    def _get_attachment_prompt(self, content: str) -> str:
        prompt = f"""
        Consider the following content, extracted from an email attachment file:
        <content>{content}</content>
        Extract relevant information to help during email classification.
        """
        return prompt    

    def _get_request_prompt(self, message: str, attachment_information: list[AttachmentInformation] = []) -> str:
        prompt = f"""
        You are an expert in processing incoming emails about updates or queries about a legal case, consider this email message:
        <message>{message}</message>
        Extract the case UUID it is related to, if any, as well as the type of email for further processing.
        """
        if attachment_information:
            prompt += f"""
            Do also consider the information extracted from the attachment files:
            <attachment-files>{[x.model_dump_json(exclude={"key"}) for x in attachment_information]}</attachment-files>
            From the attachment files, extract or make and educated guess about which legal party sent it, and to whom.
            """
        prompt += "Finally, generate an appropiate title and summary for this email message."
        return prompt

    def _get_response_prompt(self, message: str, context: str, info: list[str] = [], errors: list[str] = []) -> str:
        prompt = f"""
        Generate a formal and impersonal response in es_ES to an incoming email message related to a legal case:
        <message>{message}</message>
        """
        if self.attachments and context:
            prompt += f"""
            Do consider context extracted from attachment files:
            <context>{context}</context>
            """
        if errors and info:
            prompt += f"""
            Do consider that there were non-critical errors raised during the process of analyzing the legal case, communicate them if they are relevant.
            <errors>{errors}</errors>
            """
        elif errors:
            prompt += f"""
            IMPORTANT: There were critical errors raised during the process of analyzing the legal case, your response should be about why we cannot provide assistance.
            <errors>{errors}</errors>
            """
        if self.to_list:
            prompt += f"""
            For further customatization, consider addressing the recipient by name, if present in the list of addresses:
            <addresses>{self.to_list}</addresses>
            """
        prompt += f"""
        When answering:
         - Do not include placeholders or example information.
         - Answer as an individual, using first person.
         - If you need to identify yourself, your name is 'Asistencia', your email is {self.from_email}, and your role is that of an AI assistant working for Titan Group. 
        """
        if self.case_uuid:
            prompt += "- If there are suggestions available, redact them using terms such as 'The system suggests that ...', 'A possible response would be ...', etc."
            prompt += f"- Suggestions may also be available to download as PDF files, indicate as much and include the following HTTP link: {FRONTEND_CASE_URL_PREFIX}{self.case_uuid}"
        for item in info:
            prompt += f" - As a lawyer assistant, {item}"
        return prompt
