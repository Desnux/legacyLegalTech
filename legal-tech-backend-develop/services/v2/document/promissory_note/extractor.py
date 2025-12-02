from services.v2.document.generic import GenericExtractor
from .models import PromissoryNoteExtractorInput, PromissoryNoteExtractorOutput, PromissoryNoteInformation


class PromissoryNoteExtractor(GenericExtractor[PromissoryNoteExtractorInput, PromissoryNoteInformation, PromissoryNoteExtractorOutput]):
    """Promissory note information extractor."""

    def __init__(self, input: PromissoryNoteExtractorInput) -> None:
        super().__init__(input, PromissoryNoteInformation, PromissoryNoteExtractorOutput, label="PromissoryNote")

    def _create_prompt(self, source: str, partial_information: PromissoryNoteInformation | None) -> str:
        prompt = f"""
        Your task is to extract information from the pages of a promissory note, in order to do this consider the following source:
        <source>{source}</source>
        """
        if partial_information:
            prompt += f"""
            There is information already extracted from previous pages: <information>{partial_information.model_dump_json()}</information>
            Update the information given the new pages in the source.
            """
        prompt += """
        When extracting promissory note identifier:
        - First, check the upper right corner of the first page, as this is a common location for the identifier
        - Look for numbers that identify the promissory note, typically following patterns like:
          * "N°" or "N*" followed by numbers (e.g., "N° 12345" or "N* 891")
          * "Serie" or "Número de Serie" followed by numbers
          * "Número de Pagaré" followed by numbers
          * "PAGARÉ A PLAZO N°" followed by numbers
          * Numbers in a specific format that appear to be unique identifiers
        - Extract only the numeric part of the identifier, removing any prefixes or suffixes
        - If multiple identifiers are found, use the one that appears to be the main/primary identifier
        - If the text found is only a generic document type name (e.g., "Boleta garantía", "Pagaré"), DO NOT treat it as an identifier; instead, output an empty string
        - If you only find the beginning of an identifier (like "N°" without numbers), output an empty string
        - If no identifier is found at all, output an empty string
        - Make sure to capture the complete identifier, including any leading zeros
        - The identifier MUST consist exclusively of digits (0-9); if the text you find contains any letter or non-digit character, leave it as an empty string

        When extracting amounts:
        - Pay special attention to whether the amount appears to be handwritten or printed
        - Look for visual indicators: softer colors, less defined edges, more rounded letter shapes
        - Consider if the amount appears with different visual quality (less sharp, more organic shapes)
        - Handwritten text typically has: rounded letters, softer ink color, less precise edges, more natural curves
        - Machine-printed text typically has: sharp edges, consistent color, precise geometric shapes, uniform spacing
        - IMPORTANT: Handwritten amounts often appear next to words like "suma", "valor", "importe", "total", "monto", or similar terms
        - Look for amounts that are written in the blank space next to printed labels like "Por la suma de:", "Valor:", "Importe:", "Pagaré por:", etc.
        - In promissory notes, handwritten amounts are commonly found after phrases like "Por la suma de $", "Valor $", "Importe $", etc.
        - Set handwritten_amount to true if the amount clearly appears handwritten, false if printed/typed, or null if uncertain

        When extracting information about debtors and co-debtors (defendants):
        - Pay attention, they must be surrounded by either an identifier such as RUT or C.I.N, or labeled as a legal representative in the text.
        - Otherwise, ignore standalone names with noise in or around them, they are probably attached to signatures, in this case they are not relevant.
        - For debtors' addresses:
          * Look for phrases like "domicilio", "dirección", "reside en", "con domicilio en" near the debtor's information
          * The address usually follows the debtor's name and identifier
          * Make sure to capture the complete address including street, number, city, and any additional location details
          * If multiple addresses are mentioned, use the one that appears to be the legal/formal address
        - For debtors' legal representatives:
          * Only look for legal representatives if the debtor is an institution (e.g., company, corporation, SpA, S.A.)
          * For institutions, the legal representative is usually the "Gerente General" or similar executive position
          * Look for phrases like "representado por", "representante legal", "apoderado" near the debtor's information
          * The legal representative's information usually follows the debtor's information
          * Make sure to capture their complete information including name, identifier, occupation, and address
          * If the legal representative's address is not explicitly stated, leave as an empty string
          * If the debtor is a natural person (not an institution), do not look for a legal representative

        When extracting information about creditors and their legal representatives (plaintiffs):
        - Look for addresses near the creditor's name or identifier, they are usually labeled as "domicilio" or "dirección".
        - For creditors' legal representatives:
          * Only look for legal representatives if the creditor is an institution (e.g., company, corporation, SpA, S.A.)
          * For institutions, the legal representative is usually the "Gerente General" or similar executive position
          * Look for phrases like "representado por", "representante legal", "apoderado" near the creditor's information
          * The legal representative's information usually follows the creditor's information
          * Make sure to capture their complete information including name, identifier, occupation, and address
          * If the legal representative's address is not explicitly stated, leave as an empty string
          * If the creditor is a natural person (not an institution), do not look for a legal representative
        - Make sure to capture complete addresses including street, number, city, and any additional location details

        Important distinctions:
        - A creditor's legal representative is different from a debtor's legal representative
        - Do not confuse the roles: a creditor's representative represents the plaintiff, while a debtor's representative represents the defendant
        - Do not confuse legal representatives with sponsoring attorneys (abogados patrocinantes):
          * Legal representatives are usually executives (like Gerente General) who represent institutions
          * Sponsoring attorneys are the lawyers who will execute the legal demand
          * Sponsoring attorneys are not mentioned in the promissory note, they are assigned later
        - If a person appears as both a creditor and a debtor, they should be treated as separate entities with their respective roles
        - When in doubt about a representative's role, look for contextual clues in the text that indicate who they represent
        - Addresses are crucial for both debtors and creditors, make sure to capture them whenever they appear in the document
        - Natural persons (individuals) do not have legal representatives, only institutions do
        """
        return prompt
