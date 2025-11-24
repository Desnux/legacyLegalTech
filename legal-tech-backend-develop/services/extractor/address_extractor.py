from pydantic import BaseModel, Field

from models.pydantic import (
    PJUDAddress,
    PJUDAddressType,
    PJUDCommune,
    PJUDCommuneAntofagasta,
    PJUDCommuneAraucania,
    PJUDCommuneAricaParinacota,
    PJUDCommuneAtacama,
    PJUDCommuneAysen,
    PJUDCommuneBioBio,
    PJUDCommuneCoquimbo,
    PJUDCommuneLibertadorOHiggins,
    PJUDCommuneLosLagos,
    PJUDCommuneLosRios,
    PJUDCommuneMagallanesAntartica,
    PJUDCommuneMaule,
    PJUDCommuneMetropolitana,
    PJUDCommuneTarapaca,
    PJUDCommuneValparaiso,
    PJUDRegion,
    PJUDStreetType,
)
from services.extractor.base_extractor import BaseExtractor


class Address(BaseModel):
    region: PJUDRegion | None = Field(None, description="Chilean region")
    street_type: PJUDStreetType | None = Field(None, description="Address type, either 'avenue', 'street', or 'alleyway'")
    address_number: int | None = Field(None, description="Address number, may be None if unavailable")
    address_name: str | None = Field(None, description="Address name, may be None if unavailable")


class CommuneAntofagasta(BaseModel):
    value: PJUDCommuneAntofagasta | None = Field(None, description="Commune")


class CommuneAraucania(BaseModel):
    value: PJUDCommuneAraucania | None = Field(None, description="Commune")


class CommuneAricaParinacota(BaseModel):
    value: PJUDCommuneAricaParinacota | None = Field(None, description="Commune")


class CommuneAtacama(BaseModel):
    value: PJUDCommuneAtacama | None = Field(None, description="Commune")


class CommuneAysen(BaseModel):
    value: PJUDCommuneAysen | None = Field(None, description="Commune")


class CommuneBioBio(BaseModel):
    value: PJUDCommuneBioBio | None = Field(None, description="Commune")


class CommuneCoquimbo(BaseModel):
    value: PJUDCommuneCoquimbo | None = Field(None, description="Commune")


class CommuneLibertadorOHiggins(BaseModel):
    value: PJUDCommuneLibertadorOHiggins | None = Field(None, description="Commune")


class CommuneLosLagos(BaseModel):
    value: PJUDCommuneLosLagos | None = Field(None, description="Commune")


class CommuneLosRios(BaseModel):
    value: PJUDCommuneLosRios | None = Field(None, description="Commune")


class CommuneMagallanesAntartica(BaseModel):
    value: PJUDCommuneMagallanesAntartica | None = Field(None, description="Commune")


class CommuneMaule(BaseModel):
    value: PJUDCommuneMaule | None = Field(None, description="Commune")


class CommuneMetropolitana(BaseModel):
    value: PJUDCommuneMetropolitana | None = Field(None, description="Commune")


class CommuneTarapaca(BaseModel):
    value: PJUDCommuneTarapaca | None = Field(None, description="Commune")


class CommuneValparaiso(BaseModel):
    value: PJUDCommuneValparaiso | None = Field(None, description="Commune")


class AddressExtractor(BaseExtractor):
    def __init__(self) -> None:
        self.address_extractor_llm = self.get_structured_extractor(Address)
    
    def extract_from_text(self, text: str) -> PJUDAddress:
        address_info = self._extract_address_information(text)
        region = address_info.region or PJUDRegion.METROPOLITANA
        commune = self._extract_commune(region, text) or next(iter(region.get_commune_enum()))
        return PJUDAddress(
            region=region,
            commune=commune,
            address_type=PJUDAddressType.COMMERCIAL,
            street_type=address_info.street_type or PJUDStreetType.STREET,
            address=address_info.address_name or "",
            address_number=str(address_info.address_number) if address_info.address_number else "",
        )
    
    def _extract_commune(self, region: PJUDRegion, context: str) -> PJUDCommune | None:
        prompt = f"""
        Given the following address context: <context>{context}</context>
        Extract commune information and output the class that best represents the commune the address belongs to.
        """
        commune_enum = CommuneMetropolitana
        if region == PJUDRegion.METROPOLITANA:
            commune_enum = CommuneMetropolitana
        if region == PJUDRegion.TARAPACA:
            commune_enum = CommuneTarapaca
        if region == PJUDRegion.ANTOFAGASTA:
            commune_enum = CommuneAntofagasta
        if region == PJUDRegion.ATACAMA:
            commune_enum = CommuneAtacama
        if region == PJUDRegion.COQUIMBO:
            commune_enum = CommuneCoquimbo
        if region == PJUDRegion.VALPARAISO:
            commune_enum = CommuneValparaiso
        if region == PJUDRegion.LIBERTADOR_O_HIGGINS:
            commune_enum = CommuneLibertadorOHiggins
        if region == PJUDRegion.MAULE:
            commune_enum = CommuneMaule
        if region == PJUDRegion.BIO_BIO:
            commune_enum = CommuneBioBio
        if region == PJUDRegion.ARAUCANIA:
            commune_enum = CommuneAraucania
        if region == PJUDRegion.LOS_LAGOS:
            commune_enum = CommuneLosLagos
        if region == PJUDRegion.AYSEN:
            commune_enum = CommuneAysen
        if region == PJUDRegion.MAGALLANES_ANTARTICA:
            commune_enum = CommuneMagallanesAntartica
        if region == PJUDRegion.LOS_RIOS:
            commune_enum = CommuneLosRios
        if region == PJUDRegion.ARICA_PARINACOTA:
            commune_enum = CommuneAricaParinacota
        result = self.get_structured_extractor(commune_enum).invoke(prompt)
        if result.value is None:
            return None
        return result.value

    def _extract_address_information(self, context: str) -> Address:
        prompt = f"""
        Given the following address context: <context>{context}</context>
        Extract address information and output the classes that best represent the region and street type the address belongs to.
        """
        result: Address = self.address_extractor_llm.invoke(prompt)
        return result
