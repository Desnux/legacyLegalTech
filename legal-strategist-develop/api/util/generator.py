from models.pydantic import Locale


def int_to_roman(number: int) -> str:
    roman_numerals = {
        1: "I", 4: "IV", 5: "V", 9: "IX", 10: "X", 40: "XL", 50: "L", 
        90: "XC", 100: "C", 400: "CD", 500: "D", 900: "CM", 1000: "M"
    }
    result = ""
    for value, numeral in sorted(roman_numerals.items(), reverse=True):
        while number >= value:
            result += numeral
            number -= value
    return result


def int_to_ordinal(number: int, locale: Locale, female: bool = False):
    enumeration = {
        Locale.ES_ES: {
            1: "PRIMERA" if female else "PRIMER", 2: "SEGUNDA" if female else "SEGUNDO",
            3: "TERCERA" if female else "TERCER", 4: "CUARTA" if female else "CUARTO",
            5: "QUINTA" if female else "QUINTO", 6: "SEXTA" if female else "SEXTO",
            7: "SÉPTIMA" if female else "SÉPTIMO", 8: "OCTAVA" if female else "OCTAVO",
            9: "NOVENA" if female else "NOVENO", 10: "DÉCIMA" if female else "DÉCIMO",
        },
        Locale.EN_US: {
            1: "FIRST", 2: "SECOND", 3: "THIRD", 4: "FORTH", 5: "FIFTH",
            6: "SIXTH", 7: "SEVENTH", 8: "EIGHTH", 9: "NINTH", 10: "TENTH",
        }
    }
    return enumeration.get(locale, enumeration[Locale.EN_US]).get(number, "")
