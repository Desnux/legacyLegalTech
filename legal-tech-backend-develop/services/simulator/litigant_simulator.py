import random

from models.pydantic import Attorney


FIRST_NAMES = [
    "Juan", "María", "José", "Camila", "Francisco", "Valentina", 
    "Javier", "Catalina", "Tomás", "Antonia", "Diego", "Fernanda"
]

LAST_NAMES = [
    "González", "Muñoz", "Rojas", "Díaz", "Pérez", "Soto", 
    "Silva", "Contreras", "Espinoza", "Valenzuela", "Castro", "Vargas"
]


class LitigantSimulator:
    @classmethod
    def simulate_attorney(cls) -> Attorney:
        return Attorney(
            name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            identifier=cls.simulate_rut(),
        )

    @classmethod
    def simulate_rut(cls) -> str:
        number = random.randint(10000000, 25000000)
        verifier = random.choice("0123456789K")
        number_str = f"{number:,}".replace(",", ".")
        return f"{number_str}-{verifier}"
