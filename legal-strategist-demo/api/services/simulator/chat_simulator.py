import logging
import random
from datetime import date, timedelta

from models.pydantic import (
    Attorney,
    ChatAnswer,
    ChatMessage,
    ChatMessageSource,
    ChatSimulation,
    Defendant,
    DefendantType,
    JudicialCollectionDemandExceptionInput,
    JudicialCollectionDemandExceptionRequest,
    JudicialCollectionDemandExceptionSecondaryRequest,
    JudicialCollectionDemandTextInput,
    JudicialCollectionDispatchResolutionInput,
    LegalExceptionRequest,
    JudicialCollectionLegalRequest,
    LegalException,
    LegalSubject,
    JudicialCollectionSecondaryRequest,
    Locale,
    Plaintiff,
    SimulationInput,
    SimulationJudicialCollectionDemandExceptionInput,
    SimulationJudicialCollectionDemandTextInput,
)
from services.generator import (
    DemandExceptionGenerator,
    JudicialCollectionDemandTextGenerator,
    DispatchResolutionGenerator,
)
from services.simulator.base_simulator import BaseSimulator


class ChatSimulator(BaseSimulator):
    def __init__(self, input: SimulationInput, seed: int = 0, locale: Locale = Locale.ES_ES) -> None:
        self.simulator_input_llm = self.get_simulator_model().with_structured_output(schema=SimulationInput, method="function_calling", strict=False)
        self.simulator_demand_exception_input_llm = self.get_simulator_model().with_structured_output(
            schema=SimulationJudicialCollectionDemandExceptionInput,
            method="function_calling",
            strict=False,
        )
        self.simulator_demand_text_input_llm = self.get_simulator_model().with_structured_output(
            schema=SimulationJudicialCollectionDemandTextInput,
            method="function_calling",
            strict=False,
        )
        self.simulator_answer_llm = self.get_simulator_model().with_structured_output(schema=ChatAnswer, method="function_calling", strict=False)
        self.simulator_attorney_llm = self.get_simulator_model().with_structured_output(schema=Attorney, method="function_calling", strict=False)
        self.simulated_information: dict = {}
        self.input = input
        self.locale = locale
        self.seed = random.randint(1, 999999) if seed == 0 else seed

        try:
            generated_input = self.simulator_input_llm.invoke(self._get_prompt_input())
            self.input = generated_input
        except Exception as e:
            logging.warning(f"Could not simulate input: {e}")
    
    def simulate(self) -> ChatSimulation | None:
        self.simulated_information = {**self.input.model_dump()}

        try:
            generated_input: SimulationJudicialCollectionDemandTextInput = self.simulator_demand_text_input_llm.invoke(self._get_prompt_judicial_collection_demand_text_generator_input())
        except Exception as e:
            logging.warning(f"Could not simulate judicial collection demand text input: {e}")
            return None
        
        self.simulated_information = {
            **self.simulated_information,
            **generated_input.model_dump(),
        }
        
        main_request, secondary_requests = self._generate_plaintiff_requests()
        self.simulated_information = {
            **self.simulated_information,
            "main_request": main_request,
            "secondary_requests": [request.model_dump() for request in secondary_requests]
        }

        judicial_collection_demand_text_generator_input = JudicialCollectionDemandTextInput(
            legal_subject=LegalSubject.PROMISSORY_NOTE_COLLECTION,
            legal_representatives=generated_input.legal_representatives,
            sponsoring_attorneys=generated_input.sponsoring_attorneys,
            reasons_per_document=[],
            main_request=main_request,
            secondary_requests=secondary_requests,
        )
        judicial_collection_demand_text_generator = JudicialCollectionDemandTextGenerator(
            input=judicial_collection_demand_text_generator_input,
            seed=self.seed,
            locale=self.locale,
        )
        demand_text = judicial_collection_demand_text_generator.generate_from_simulation(self.input)

        messages: list[ChatMessage] = []

        if demand_text:
            messages.append(ChatMessage(source=ChatMessageSource.PLAINTIFFS, content=demand_text.text))
        else:
            logging.warning("Could not simulate demand text generation")
            return ChatSimulation(messages=messages, simulated_information=self.simulated_information, seed=self.seed)
        
        judicial_collection_dispatch_resolution_generator_input = self._generate_judicial_collection_dispatch_resolution_generator_input()
        self.simulated_information["court_number"] = judicial_collection_dispatch_resolution_generator_input.court_number
        self.simulated_information["case_role"] = judicial_collection_dispatch_resolution_generator_input.case_role
        self.simulated_information["case_title"] = judicial_collection_dispatch_resolution_generator_input.case_title
        self.simulated_information["demand_text_date"] = judicial_collection_dispatch_resolution_generator_input.demand_text_date
        self.simulated_information["dispatch_resolution_date"] = judicial_collection_dispatch_resolution_generator_input.issue_date
        judicial_collection_dispatch_resolution_generator = DispatchResolutionGenerator(
            input=judicial_collection_dispatch_resolution_generator_input,
            seed=self.seed,
            locale=self.locale,
        )
        dispatch_resolution = judicial_collection_dispatch_resolution_generator.generate_from_text(demand_text.text)

        if dispatch_resolution:
            messages.append(ChatMessage(source=ChatMessageSource.COURT, content=dispatch_resolution.text))
        else:
            logging.warning("Could not simulate dispatch resolution generation")
            return ChatSimulation(messages=messages, simulated_information=self.simulated_information, seed=self.seed)
        
        judicial_collection_demand_exception_generator_input = self._generate_judicial_collection_demand_exception_generator_input()
        self.simulated_information["defendant_attorneys"] = judicial_collection_demand_exception_generator_input.defendant_attorneys
        judicial_collection_demand_exception_generator = DemandExceptionGenerator(
            input=judicial_collection_demand_exception_generator_input,
            seed=self.seed,
            locale=self.locale,
        )
        demand_exception = judicial_collection_demand_exception_generator.generate_from_text(demand_text.text)

        if demand_exception:
            messages.append(ChatMessage(source=ChatMessageSource.DEFENDANTS, content=demand_exception.text))
        else:
            logging.warning("Could not simulate demand_exception generation")
            return ChatSimulation(messages=messages, simulated_information=self.simulated_information, seed=self.seed)

        return ChatSimulation(messages=messages, simulated_information=self.simulated_information, seed=self.seed)
    
    def _generate_judicial_collection_demand_exception_generator_input(self) -> JudicialCollectionDemandExceptionInput:
        try:
            generated_input: SimulationJudicialCollectionDemandExceptionInput = self.simulator_demand_exception_input_llm.invoke(self._get_prompt_judicial_collection_demand_exception_generator_input())
        except Exception as e:
            logging.warning(f"Could not simulate demand exception input: {e}")
            generated_input = SimulationJudicialCollectionDemandExceptionInput(defendant_attorneys=None)

        plaintiffs: list[Plaintiff] = []
        for creditor in self.input.creditors or []:
            plaintiffs.append(Plaintiff(name=creditor.name, identifier=creditor.identifier))

        defendants: list[Defendant] = []
        for debtor in self.input.debtors:
            defendants.append(Defendant(
                name=debtor.name,
                identifier=debtor.identifier,
                occupation=None,
                address=debtor.address,
                legal_representatives=debtor.legal_representatives,
                type=DefendantType.DEBTOR,
            ))
        for debtor in self.input.co_debtors:
            defendants.append(Defendant(
                name=debtor.name,
                identifier=debtor.identifier,
                occupation=None,
                address=debtor.address,
                legal_representatives=debtor.legal_representatives,
                type=DefendantType.CO_DEBTOR,
            ))

        exceptions, secondary_requests = self._generate_defendant_exceptions_and_requests()

        return JudicialCollectionDemandExceptionInput(
            court_city=self.input.court_city,
            court_number=self.simulated_information["court_number"],
            case_role=self.simulated_information["case_role"],
            case_title=self.simulated_information["case_title"],
            plaintiffs=plaintiffs,
            plaintiff_attorneys=self.simulated_information["sponsoring_attorneys"],
            defendants=defendants,
            defendant_attorneys=generated_input.defendant_attorneys,
            demand_text_date=self.simulated_information["demand_text_date"],
            exceptions=exceptions,
            secondary_requests=secondary_requests,
        )

    def _generate_judicial_collection_dispatch_resolution_generator_input(self) -> JudicialCollectionDispatchResolutionInput:
        local_random = random.Random(self.seed if self.seed != 0 else None)
        current_date = date.today()

        prompt = f"""Generate a concise title in {self.locale} in less than 10 words for a legal case that involves the following entities:
        - Plaintiffs: {[creditor.name for creditor in self.input.creditors or []]}
        - Defendants: {[debtor.name for debtor in self.input.debtors or []]}

        Generate this data in a format that can easily be used for simulation purposes, and ensure the data looks realistic and valid for use in a Chilean legal context.
        """
        answer: ChatAnswer = self.simulator_answer_llm.invoke(prompt)

        return JudicialCollectionDispatchResolutionInput(
            court_city=self.input.court_city,
            court_number=local_random.randint(1, 10),
            case_role=f"C-{local_random.randint(100, 9999)}-{current_date.year}",
            case_title=answer.answer,
            issue_date=current_date,
            demand_text_date=current_date - timedelta(days=local_random.randint(5, 25)),
            requirements=[],
        )

    def _generate_defendant_exceptions_and_requests(self) -> tuple[list[JudicialCollectionDemandExceptionRequest], list[JudicialCollectionDemandExceptionSecondaryRequest]]:
        local_random = random.Random(self.seed if self.seed != 0 else None)
        current_date = date.today()

        exception_requests: list[JudicialCollectionDemandExceptionRequest] = []
        available_exceptions = list(LegalException)
        num_exceptions = random.randint(1, 3)
        selected_exceptions = random.sample(available_exceptions, num_exceptions)
        for selected_exception in selected_exceptions:
            exception_requests.append(JudicialCollectionDemandExceptionRequest(nature=selected_exception, context=None))

        secondary_requests: list[JudicialCollectionDemandExceptionSecondaryRequest] = []
        secondary_amount = local_random.randint(1, 5)
        available_natures = list(LegalExceptionRequest)

        delegate: Attorney | None = None
        if secondary_amount > available_natures.index(LegalExceptionRequest.SPONSORSHIP_AND_POWER):
            prompt = f"""
            Generate the following attributes for a defendant attorney:
            - Name: Generate name for the defendant attorney, which must be a natural person.
            - RUT Identifier: Provide valid Chilean RUT number for the defendant attorney in the format XX.XXX.XXX-X.
            - Address: Provide a realistic address for the defendant attorney.

            Generate this data in a format that can easily be used for simulation purposes, and ensure the data looks realistic and valid for use in a Chilean legal context.
            """
            delegate = self.simulator_attorney_llm.invoke(prompt)

        for idx in range(secondary_amount):
            nature = available_natures[idx]
            context = None
            if nature == LegalExceptionRequest.INCLUDE_DOCUMENTS:
                document_date = current_date - timedelta(days=local_random.randint(60, 400))
                #TODO (improve with ML examples?)
                continue

            elif nature in [LegalExceptionRequest.INDICATE_EMAILS]:
                consider = local_random.choice([True, False])
                if not consider:
                    continue
                if nature == LegalExceptionRequest.INDICATE_EMAILS:
                    prompt = f"Generate an email address for each defendant attorney: <defendant_attorneys>{self.simulated_information.get('defendant_attorneys', [])}</defendant_attorneys>"
                    if delegate:
                        prompt += f"\nAlso generate an email address for each delegate attorney: <delegate_attorneys>[{delegate.name}]</delegate_attorneys>"
                    prompt += "\nGenerate this data in a format that can easily be used for simulation purposes, and ensure the data looks realistic and valid for use in a Chilean legal context."
                    answer: ChatAnswer = self.simulator_answer_llm.invoke(prompt)
                    if answer.answer:
                        context = f"Attorney emails: {answer.answer}"
            secondary_requests.append(JudicialCollectionDemandExceptionSecondaryRequest(nature=nature, context=context))
        return exception_requests, secondary_requests

    def _generate_plaintiff_requests(self) -> tuple[str, list[JudicialCollectionSecondaryRequest]]:
        local_random = random.Random(self.seed if self.seed != 0 else None)
        if self.locale == Locale.EN_US:
            main_request = local_random.choice([
                "TOTAL EXECUTION AND SEIZURE OF UNPAID OBLIGATIONS",
                "EXECUTIVE DEMAND AND REQUEST THAT AN EXECUTION AND SEIZURE ORDER BE ISSUED",
            ])
        else:
            main_request = local_random.choice([
                "EJECUCION Y EMBARGO TOTAL DE LAS OBLIGACIONES INSOLUTAS",
                "DEMANDA EJECUTIVA Y SOLICITA SE DESPACHE MANDAMIENTO DE EJECUCIÓN Y EMBARGO",
            ])

        secondary_requests: list[JudicialCollectionSecondaryRequest] = []
        secondary_amount = local_random.randint(2, 7)
        available_natures = list(JudicialCollectionLegalRequest)

        delegate: Attorney | None = None
        if secondary_amount > available_natures.index(JudicialCollectionLegalRequest.SPONSORSHIP_AND_POWER):
            prompt = f"""
            Generate the following attributes for an sponsoring attorney:
            - Name: Generate name for the sponsoring attorney, which must be a natural person.
            - RUT Identifier: Provide valid Chilean RUT number for the sponsoring attorney in the format XX.XXX.XXX-X.
            - Address: Provide a realistic address for the sponsoring attorney.

            Generate this data in a format that can easily be used for simulation purposes, and ensure the data looks realistic and valid for use in a Chilean legal context.
            """
            delegate = self.simulator_attorney_llm.invoke(prompt)

        for idx in range(secondary_amount):
            nature = available_natures[idx]
            context = None
            if nature == JudicialCollectionLegalRequest.INCLUDE_DOCUMENTS:
                if self.locale == Locale.EN_US:
                    context = local_random.choice([
                        "Copy of the promissory notes identified in the main part of this presentation, which correspond to the founding titles of this execution,",
                        "Consider the following as the founding document of this execution, and arrange for the custody of the identified promissory notes."
                    ])
                else:
                    context = local_random.choice([
                        "Copia de los pagarés singularizados en lo principal de esta presentación, que corresponden a los títulos fundantes de esta ejecución",
                        "Sírvase SS. tener por acompañados como documento fundante de esta ejecución el que a continuación se indica, y disponer la custodia de los pagarés singularizados",
                    ])
            elif nature in [JudicialCollectionLegalRequest.INDICATE_EMAILS, JudicialCollectionLegalRequest.REQUEST_EXHORTATION]:
                consider = local_random.choice([True, False])
                if not consider:
                    continue
                if nature == JudicialCollectionLegalRequest.INDICATE_EMAILS:
                    prompt = f"Generate an email address for each sponsoring attorney: <sponsoring_attorneys>{self.simulated_information.get('sponsoring_attorneys', [])}</sponsoring_attorneys>"
                    if delegate:
                        prompt += f"\nAlso generate an email address for each delegate attorney: <delegate_attorneys>[{delegate.name}]</delegate_attorneys>"
                    prompt += "\nGenerate this data in a format that can easily be used for simulation purposes, and ensure the data looks realistic and valid for use in a Chilean legal context."
                    answer: ChatAnswer = self.simulator_answer_llm.invoke(prompt)
                    if answer.answer:
                        context = f"Attorney emails: {answer.answer}"
                elif nature == JudicialCollectionLegalRequest.REQUEST_EXHORTATION:
                    prompt = f"""Generate information about a singular external court with the following attributes:
                        - City: City where the court is located (must be different from {self.input.court_city}).
                        - Type: Either 'Civil' or 'de Letras'. 
                        - Number: If 'Civil', assign a random number between 1 and 10 (inclusive).
                        - Reason: The reason to involve the external court in legal matters, by default, because one or more defendants have one or more of their official addresses in their city.
                    
                        Consider this examples, do not copy information from the examples: <examples>[19° Juzgado Civil de Santiago, Juzgado de Letras de Colina]</examples>
                        """
                    prompt += "\nGenerate this data in a format that can easily be used for simulation purposes, and ensure the data looks realistic and valid for use in a Chilean legal context."
                    answer: ChatAnswer = self.simulator_answer_llm.invoke(prompt)
                    if answer.answer:
                        context = f"External court information: {answer.answer}"
            secondary_requests.append(JudicialCollectionSecondaryRequest(nature=nature, context=context))
        return main_request, secondary_requests

    def _get_prompt_input(self) -> str:
        prompt = """
        Generate a list of creditors, debtors, and co-debtors with the following attributes:

        Creditors:
        - Name: Generate realistic Chilean names for creditors, which can be either natural people or companies.
        - RUT Identifier: Provide valid Chilean RUT numbers for each creditor in the format XX.XXX.XXX-X.

        Debtors and Co-debtors:
        - Name: Generate names for debtors, which can be either natural people or companies.
        - RUT Identifier: Provide valid Chilean RUT numbers for each debtor in the format XX.XXX.XXX-X.
        - Address: Provide a realistic address for each debtor and co-debtor.
        - Legal Representatives (only for companies): If the debtor is a company, generate 1-2 legal representatives with the following details:
            - Name: Generate realistic names for the legal representatives.
            - RUT Identifier: Provide a valid Chilean RUT number for each legal representative.
            - Occupation: Include an occupation or profession for each legal representative.
            - Address: Provide a realistic address for each legal representative.
        
        Include co-debtors where relevant, with similar details to the debtor.

        Generate this data in a format that can easily be used for simulation purposes, and ensure the data looks realistic and valid for use in a Chilean legal context.
        """
        prompt += f"\nThe user may have contributed data that they want to use, if they did, use it and generate the missing information: <user_data>{self.input}</user_data>"
        return prompt
    
    def _get_prompt_judicial_collection_demand_text_generator_input(self) -> str:
        plaintiffs: list[dict] = []
        for creditor in self.input.creditors or []:
            plaintiffs.append(creditor.model_dump())

        prompt = f"""
        Consider the following plaintiffs that want to start a judicial collection legal case in {self.input.court_city}: <plaintiffs>{plaintiffs}</plaintiffs>

        Generate a list of legal representatives and sponsoring attorneys for the plaintiffs, with the following attributes:

        Legal Representatives:
        - Name: Generate names for legal representatives, which must be natural people.
        - RUT Identifier: Provide valid Chilean RUT numbers for each legal representative in the format XX.XXX.XXX-X.
        - Occupation: Include an occupation or profession for each legal representative.
        - Address: Provide a realistic address for each legal representative.

        Sponsoring Attorneys:
        - Name: Generate names for sponsoring attorneys, which must be natural people.
        - RUT Identifier: Provide valid Chilean RUT numbers for each sponsoring attorney in the format XX.XXX.XXX-X.
        - Address: Provide a realistic address for each sponsoring attorney.

        Generate this data in a format that can easily be used for simulation purposes, and ensure the data looks realistic and valid for use in a Chilean legal context.
        """
        return prompt
    
    def _get_prompt_judicial_collection_demand_exception_generator_input(self) -> str:
        defendants: list[dict] = []
        for debtor in (self.input.debtors or []) + (self.input.co_debtors or []):
            defendants.append(debtor.model_dump())

        prompt = f"""
        Consider the following defendants that want to halt a judicial collection legal case in {self.input.court_city}: <defendants>{defendants}</defendants>

        Generate a list of defendant attorneys for the defendants, with the following attributes:

        Defendant Attorneys:
        - Name: Generate names for defendant attorneys, which must be natural people.
        - RUT Identifier: Provide valid Chilean RUT numbers for each defendant attorney in the format XX.XXX.XXX-X.
        - Address: Provide a realistic address for each defendant attorney.

        Generate this data in a format that can easily be used for simulation purposes, and ensure the data looks realistic and valid for use in a Chilean legal context.
        """
        return prompt
    