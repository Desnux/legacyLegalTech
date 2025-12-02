import logging
import time
from concurrent.futures import ThreadPoolExecutor

from models.pydantic import Analysis, AnalysisStatus, AnalysisTag, MissingPaymentDocumentType
from services.v2.document.base import BaseAnalyzer, Metrics
from .missing_payment_argument import MissingPaymentArgumentStructure
from .models import DemandTextAnalysis, DemandTextAnalyzerInput, DemandTextAnalyzerOutput


class DemandTextAnalyzer(BaseAnalyzer):
    """Demand text analyzer."""

    def __init__(self, input: DemandTextAnalyzerInput, control: DemandTextAnalyzerInput | None = None) -> None:
        super().__init__()
        self.input = input
        self.control = control
        self.analyzer = self._create_structured_analyzer(Analysis)

    def analyze(self) -> DemandTextAnalyzerOutput:
        """Analyzes a demand text on its own or compared to a expected result."""
        metrics = Metrics(label=f"DemandTextAnalyzer.analyze", llm_invocations=7)
        start_time = time.time()

        with ThreadPoolExecutor() as executor:
            if control := self.control:
                future_to_analysis = {
                    "header": executor.submit(self._analyze_header, self.input.header, control.header),
                    "summary": executor.submit(self._analyze_summary, self.input.summary, control.summary),
                    "court": executor.submit(self._analyze_court, self.input.court, control.court),
                    "opening": executor.submit(self._analyze_opening, self.input.opening, control.opening),
                    "missing_payment_arguments": executor.submit(
                        self._analyze_missing_payment_arguments,
                        self.input.missing_payment_arguments or [],
                        control.missing_payment_arguments if control else None,
                    ),
                    "main_request": executor.submit(self._analyze_main_request, self.input.main_request, control.main_request),
                    "additional_requests": executor.submit(self._analyze_additional_requests, self.input.additional_requests, control.additional_requests),
                }
            else:
                future_to_analysis = {
                    "header": executor.submit(self._analyze_header, self.input.header),
                    "summary": executor.submit(self._analyze_summary, self.input.summary),
                    "court": executor.submit(self._analyze_court, self.input.court),
                    "opening": executor.submit(self._analyze_opening, self.input.opening),
                    "missing_payment_arguments": executor.submit(
                        self._analyze_missing_payment_arguments,
                        self.input.missing_payment_arguments or [],
                    ),
                    "main_request": executor.submit(self._analyze_main_request, self.input.main_request),
                    "additional_requests": executor.submit(self._analyze_additional_requests, self.input.additional_requests),
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
        Generate a final analysis in es_ES combining elements of each one, use the mean score, and use the lowest status of them all.
        """
        try:
            overall_analysis = self.analyzer.invoke(prompt)
        except Exception as e:
            logging.warning(f"Could not generate an overall analysis: {e}")

        analysis = DemandTextAnalysis(
            header=results["header"],
            summary=results["summary"],
            court=results["court"],
            opening=results["opening"],
            missing_payment_arguments=results["missing_payment_arguments"],
            main_request=results["main_request"],
            additional_requests=results["additional_requests"],
            overall=overall_analysis,
        )

        metrics.time = round(time.time() - start_time, 4)
        return DemandTextAnalyzerOutput(metrics=metrics, structured_output=analysis)

    def _analyze_content(self, input: str | None, control: str | None, content_guidelines: str) -> Analysis | None:
        if not input:
            return Analysis(tags=[AnalysisTag.MISSING_INFO], status=AnalysisStatus.ERROR, score=0.0)
        if len(input.strip()) == 0:
            return Analysis(tags=[AnalysisTag.MISSING_INFO], status=AnalysisStatus.ERROR, score=0.0)
        prompt = f"""
        Provide an analysis in es_ES of the following generated content:
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
            analysis: Analysis = self.analyzer.invoke(prompt)
        except Exception as e:
            logging.warning(f"Could not perform analysis: {e}")
            return None
        return analysis
    
    def _analyze_header(self, input: str | None, control: str | None = None) -> Analysis | None:
        content_guidelines = """
        The content should:
          - Indicate procedure
          - Indicate subject
          - Indicate plaintiffs, each one a name followed by a RUT and their address
          - Indicate sponsoring attorneys, each one a name followed by a RUT
          - Indicate defendants, each one a name followed by a RUT, their address, and a legal representative (only if they are a group or institution)
        Raise warnings if:
          - There are similar or repeated names across attorneys
          - There are similar or repeated names across defendants
          - There are similar or repeated names across plaintiffs
          - There are similar or repeated names across legal representatives of the same defendant
          - A group or institution is used as a legal representative instead of a regular person
          - There are possible OCR errors in names, usually strange combinations of characters with many diacritics
          - Any plaintiff or defendant is missing their address
          - Addresses are incomplete (should include street, number, city, and any additional location details)
        Ignore warnings if:
          - The only similar names correspond to legal representatives that are also defendants
        If all warnings can be ignored use 'good' as analysis status
        """
        return self._analyze_content(input, control, content_guidelines)

    def _analyze_summary(self, input: str | None, control: str | None = None) -> Analysis | None:
        content_guidelines = """
        The content should:
          - List a main request, followed by zero or more additional requests
          - Each additional request should be short and written in an impersonal tone
          - Each additional request should be a summary, they should not include specific goods, people, documents, or locations
        """
        return self._analyze_content(input, control, content_guidelines)
    
    def _analyze_court(self, input: str | None, control: str | None = None) -> Analysis | None:
        content_guidelines = """
        The content should:
          - Indicate a real court in a real city
          - Use common abbreviations, such as S.J.L for "Juzgado de Letras"
        """
        return self._analyze_content(input, control, content_guidelines)
    
    def _analyze_opening(self, input: str | None, control: str | None = None) -> Analysis | None:
        content_guidelines = """
        The content should:
          - Indicate a sponsoring attorney, who is the author of the content
          - Indicate plaintiffs and their legal representatives if they are groups or institutions, there must be RUT identifiers and real addresses associated with them
          - Indicate the main request of the content
          - Indicate defendants, they may be debtors or co-debtors, there must be RUT identifiers and real addresses associated with them
          - End abruptly before starting to list relevant documents, this are part of another section, do not consider them as missing info
        """
        return self._analyze_content(input, control, content_guidelines)
    
    def _analyze_missing_payment_arguments(self, input: list[MissingPaymentArgumentStructure], control: list[MissingPaymentArgumentStructure] | None = None) -> list[Analysis] | None:
        if len(input) == 0:
            return [Analysis(tags=[AnalysisTag.MISSING_INFO], status=AnalysisStatus.ERROR, score=0.0)]
        control_arguments = []
        if control:
            control_arguments = [segment.argument for segment in control]
        promissory_note_content_guidelines = """
        The content should:
        - Begin with the word 'Pagaré' followed by an identifier. The identifier can be:
            - Numeric, e.g., 'Pagaré a plazo N° 123'
            - A name composed of at least two words before the term 'suscrito', e.g., 'Pagaré boleta garantía en pesos, suscrito'
        - Contain the term 'suscrito' at some point in the document.
        - Indicate the creation date, creditor, and total amount.
        - Indicate if the amount should be paid in one or multiple installments; if multiple, provide the number of installments, the amount per installment, and the frequency of payment.
        - Explain the relevance of this document to a missing payments legal case by detailing the debtor's actions and specifying the pending amount.
        Raise a warning if:
        - The document does not start with 'Pagaré' followed by a valid identifier (numeric or descriptive) or is missing the term 'suscrito'.
        """
        bill_guidelines = """
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

    def _analyze_main_request(self, input: str | None, control: str | None = None) -> Analysis | None:
        content_guidelines = """
        The content should:
          - Indicate relevant legal articles
          - Request that the court consider a demand against explicitly mentioned defendants, either debtors or co-debtors
          - Indicate the total amount in dispute, both in numbers and how it would be read aloud
        """
        return self._analyze_content(input, control, content_guidelines)
    
    def _analyze_additional_requests(self, input: str | None, control: str | None = None) -> Analysis | None:
        content_guidelines = """
        The content should:
          - Be a list of additional requests.
          - Use an impersonal and formal tone.
        """
        return self._analyze_content(input, control, content_guidelines)
