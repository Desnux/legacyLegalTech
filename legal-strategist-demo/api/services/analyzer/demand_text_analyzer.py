import logging
import os
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor

from fastapi import UploadFile
from pydantic import BaseModel, Field

from models.pydantic import (
    Analysis,
    AnalysisStatus,
    AnalysisTag,
    JudicialCollectionDemandTextAnalysis,
    JudicialCollectionDemandTextStructure,
    Locale,
    MissingPaymentArgument,
    MissingPaymentDocumentType,
)
from services.analyzer.base_analyzer import BaseAnalyzer
from services.loader import PdfLoader


class Structure(BaseModel):
    header: str | None = Field(None, description="Demand text header, includes procedure, subject, plaintiffs, sponsoring attorneys, defendants, and legal representatives of the defendants")
    summary: str | None = Field(None, description="Demand text summary, includes main request, and additional requests called OTROSI, in order")
    court: str | None = Field(None, description="Demand text court info, includes city and court abbreviation, such as S.J.L")
    opening: str | None = Field(None, description="Demand text opening paragraphs")
    missing_payment_arguments: list[MissingPaymentArgument] | None = Field(None, description="Demant text missing payment arguments, each one is enumerated and includes an identifier, amount, creditors, debtors, etc.")
    main_request: str | None = Field(None, description="Demand text main request")
    additional_requests: str | None = Field(None, description="Demand text additional requests")


class DemandTextAnalyzer(BaseAnalyzer):
    def __init__(self, locale: Locale = Locale.ES_ES) -> None:
        self.analysis_llm = self.get_structured_analyzer(Analysis)
        self.structure_llm = self.get_structured_analyzer(Structure)
        self.locale = locale

    def analyze_from_files(self, input: UploadFile, control: UploadFile | None) -> JudicialCollectionDemandTextAnalysis | None:
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_input_file:
                shutil.copyfileobj(input.file, temp_input_file)
                temp_input_file_path = temp_input_file.name

                try:
                    with tempfile.NamedTemporaryFile(delete=False) as temp_control_file:
                        shutil.copyfileobj(control.file, temp_control_file)
                        temp_control_file_path = temp_control_file.name
                        return self._analyze_from_file_path(temp_input_file_path, temp_control_file_path)
                except Exception as e:
                    logging.warning(f"Error processing document ({type(e).__name__}): {e}")
                    return None
                finally:
                    if temp_control_file_path and os.path.exists(temp_control_file_path):
                        os.remove(temp_control_file_path)

        except Exception as e:
            logging.warning(f"Error processing document ({type(e).__name__}): {e}")
            return None
        finally:
            if temp_input_file_path and os.path.exists(temp_input_file_path):
                os.remove(temp_input_file_path)
        return None
    
    def analyze_from_mixed(self, input: JudicialCollectionDemandTextStructure, control: UploadFile) -> JudicialCollectionDemandTextAnalysis | None:
        temp_control_file_path = ""
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_control_file:
                shutil.copyfileobj(control.file, temp_control_file)
                temp_control_file_path = temp_control_file.name
                return self._analyze_from_mixed(input, temp_control_file_path)
        except Exception as e:
            logging.warning(f"Error processing document ({type(e).__name__}): {e}")
            return None
        finally:
            if temp_control_file_path and os.path.exists(temp_control_file_path):
                os.remove(temp_control_file_path)
        return None

    def analyze_from_structured(self, input: JudicialCollectionDemandTextStructure, control: JudicialCollectionDemandTextStructure | None) -> JudicialCollectionDemandTextAnalysis | None:
        with ThreadPoolExecutor() as executor:
            future_to_analysis = {
                "header": executor.submit(self._analyze_header, input.header or "", control.header if control else None),
                "summary": executor.submit(self._analyze_summary, input.summary or "", control.summary if control else None),
                "court": executor.submit(self._analyze_court, input.court or "", control.court if control else None),
                "opening": executor.submit(self._analyze_opening, input.opening or "", control.opening if control else None),
                "missing_payment_arguments": executor.submit(
                    self._analyze_missing_payment_arguments,
                    input.missing_payment_arguments or [],
                    control.missing_payment_arguments if control else None,
                ),
                "main_request": executor.submit(self._analyze_main_request, input.main_request or "", control.main_request if control else None),
                "additional_requests": executor.submit(self._analyze_additional_requests, input.additional_requests or "", control.additional_requests if control else None, input.summary),
            }
            results = {}
            results_dump = {}
            for key, future in future_to_analysis.items():
                result: Analysis | list[Analysis] = future.result()
                results[key] = result
                if isinstance(result, list):
                    results_dump[key] = [item.model_dump_json() for item in result]
                elif result is not None:
                    results_dump[key] = result.model_dump_json()
                else:
                    results_dump[key] = None

        overall_analysis: Analysis | None = None
        prompt = f"""
        Consider this list of analysis results:
        <results>{results_dump}</result>
        Generate a final analysis in {self.locale} combining elements of each one, use the mean score, and use the lowest status of them all
        """
        try:
            overall_analysis = self.analysis_llm.invoke(prompt)
        except Exception as e:
            logging.warning(f"Could not generate an overall analysis: {e}")

        analysis = JudicialCollectionDemandTextAnalysis(
            header=results["header"],
            summary=results["summary"],
            court=results["court"],
            opening=results["opening"],
            missing_payment_arguments=results["missing_payment_arguments"],
            main_request=results["main_request"],
            additional_requests=results["additional_requests"],
            overall=overall_analysis,
        )
        return analysis

    def _analyze_from_file_path(self, input: str, control: str) -> JudicialCollectionDemandTextAnalysis | None:
        loader = PdfLoader(input)
        input_documents = loader.load_no_ocr()
        if len(input_documents) == 0:
            return None
        loader = PdfLoader(control)
        control_documents = loader.load_no_ocr()
        if len(control_documents) == 0:
            return None
        
        prompt = f"""
        Consider the following demand text context:
        <context>{' '.join([document.page_content for document in input_documents])}</context>
        Divide it by sections, each section must include the relevant information.
        """
        input_structure: Structure = self.structure_llm.invoke(prompt)

        prompt = f"""
        Consider the following demand text context:
        <context>{' '.join([document.page_content for document in control_documents])}</context>
        Divide it by sections, each section must include the relevant information.
        """
        control_structure: Structure = self.structure_llm.invoke(prompt)

        return self.analyze_from_structured(
            JudicialCollectionDemandTextStructure(**input_structure.model_dump()),
            JudicialCollectionDemandTextStructure(**control_structure.model_dump()),
        )   

    def _analyze_from_mixed(self, input: JudicialCollectionDemandTextStructure, control: str) -> JudicialCollectionDemandTextAnalysis | None:
        loader = PdfLoader(control)
        control_documents = loader.load_no_ocr()
        if len(control_documents) == 0:
            return None
        
        prompt = f"""
        Consider the following demand text context:
        <context>{' '.join([document.page_content for document in control_documents])}</context>
        Divide it by sections, each section must include the relevant information.
        """
        control_structure: Structure = self.structure_llm.invoke(prompt)

        return self.analyze_from_structured(
            JudicialCollectionDemandTextStructure(**input.model_dump()),
            JudicialCollectionDemandTextStructure(**control_structure.model_dump()),
        )   

    def _analyze_content(self, input: str, control: str | None, content_guidelines: str) -> Analysis | None:
        if len(input.strip()) == 0:
            return Analysis(tags=[AnalysisTag.MISSING_INFO], status=AnalysisStatus.ERROR, score=0.0)
        prompt = f"""
        Provide an analysis in {self.locale} of the following generated content:
        <content>{input}</content>
        {content_guidelines}
        """
        if control:
            prompt += f"""
            Additionally, the content should have the same information as this control data:
            <data>{control}</data>
            Raise warnings if:
              - There is missing, incorrect, or additional information
            """
        prompt += """
        When answering:
          - Use an impersonal tone
        """
        try:
            analysis: Analysis = self.analysis_llm.invoke(prompt)
        except Exception as e:
            logging.warning(f"Could not perform analysis: {e}")
            return None
        return analysis
    
    def _analyze_header(self, input: str, control: str | None) -> Analysis | None:
        content_guidelines = """
        The content should:
          - Indicate procedure
          - Indicate subject
          - Indicate plaintiffs, each one a name followed by a RUT
          - Indicate sponsoring attorneys, each one a name followed by a RUT
          - Indicate defendants, each one a name followed by a RUT and a legal representative (only if they are a group or institution)
        Raise warnings if:
          - There are similar or repeated names across attorneys
          - There are similar or repeated names across defendants
          - There are similar or repeated names across plaintiffs
          - There are similar or repeated names across legal representatives of the same defendant
          - A group or institution is used as a legal representative instead of a regular person
          - There are possible OCR errors in names, usually strange combinations of characters with many diacritics
        Ignore warnings if:
          - The only similar names correspond to legal representatives that are also defendants
        If all warnings can be ignored use 'good' as analysis status
        """
        return self._analyze_content(input, control, content_guidelines)

    def _analyze_summary(self, input: str, control: str | None) -> Analysis | None:
        content_guidelines = """
        The content should:
          - List a main request, followed by zero or more additional requests
          - Each additional request should be short and written in an impersonal tone
          - Each additional request should be a summary, they should not include specific goods, people, documents, or locations
        """
        return self._analyze_content(input, control, content_guidelines)
    
    def _analyze_court(self, input: str, control: str | None) -> Analysis | None:
        content_guidelines = """
        The content should:
          - Indicate a real court in a real city
          - Use common abbreviations, such as S.J.L for "Juzgado de Letras"
        """
        return self._analyze_content(input, control, content_guidelines)
    
    def _analyze_opening(self, input: str, control: str | None) -> Analysis | None:
        content_guidelines = """
        The content should:
          - Indicate a sponsoring attorney, who is the author of the content
          - Indicate plaintiffs and their legal representatives if they are groups or institutions, there must be RUT identifiers and real addresses associated with them
          - Indicate the main request of the content
          - Indicate defendants, they may be debtors or co-debtors, there must be RUT identifiers and real addresses associated with them
          - End abruptly before starting to list relevant documents, this are part of another section, do not consider them as missing info
        """
        return self._analyze_content(input, control, content_guidelines)
    
    def _analyze_missing_payment_arguments(self, input: list[MissingPaymentArgument], control: list[MissingPaymentArgument] | None) -> list[Analysis] | None:
        if len(input) == 0:
            return [Analysis(tags=[AnalysisTag.MISSING_INFO], status=AnalysisStatus.ERROR, score=0.0)]
        control_arguments = []
        if control:
            control_arguments = [segment.argument for segment in control]
        promissory_note_content_guidelines = f"""
        The content should:
          - Indicate a document and provide its numeric identifier 
          - Indicate creation date, creditor, and total amount
          - Indicate if the amount should be paid in one or multiple installments, in case of multiple, it should indicate how many, amount per installment, and frequency of payment
          - Indicate why this document is relevant to a missing payments legal case, this should include debtor actions and pending amount
        Raise a warning if:
          - The document lacks a numeric identifier
        """
        bill_guidelines = f"""
        The content should:
          - Indicate a document and provide its numeric identifier 
          - Indicate creation date, creditor, debtor, and total amount
          - Indicate why this document is relevant to a missing payments legal case, this should include debtor actions and pending amount
        Raise a warning if:
          - The document lacks a numeric identifier
        """
        analysis_list: list[Analysis] = []
        for i, argument_obj in enumerate(input):
            content_guidelines = promissory_note_content_guidelines if argument_obj.document_type == MissingPaymentDocumentType.PROMISSORY_NOTE else bill_guidelines
            if i >= len(control_arguments) > 0:
                analysis = Analysis(tags=[AnalysisTag.FALSE_INFORMATION], status=AnalysisStatus.ERROR, score=0.0)
            else:
                analysis = self._analyze_content(argument_obj.argument, control_arguments[i] if i < len(control_arguments) else None, content_guidelines)
            analysis_list.append(analysis)
        if len(control_arguments) > len(input):
          for i in range(len(control_arguments) - len(input)):
              analysis_list.append(Analysis(tags=[AnalysisTag.MISSING_INFO], status=AnalysisStatus.ERROR, score=0.0))
        return analysis_list

    def _analyze_main_request(self, input: str, control: str | None) -> Analysis | None:
        content_guidelines = """
        The content should:
          - Indicate relevant legal articles
          - Request that the court consider a demand against explicitly mentioned defendants, either debtors or co-debtors
          - Indicate the total amount in dispute, both in numbers and how it would be read aloud
        """
        return self._analyze_content(input, control, content_guidelines)
    
    def _analyze_additional_requests(self, input: str, control: str | None, summary: str | None) -> Analysis | None:
        content_guidelines = """
        The content should:
          - Be a list of additional requests
          - Use an impersonal and formal tone
        """
        if summary:
            content_guidelines += f"""
            Additionally, each item should match, in order and content, the short version of each request presented in this summary:
            <summary>{summary}</summary>
            """
        return self._analyze_content(input, control, content_guidelines)
