from enum import Enum

from pydantic import BaseModel, Field, model_validator


class PJUDCommune(Enum):
    pass


class PJUDRegion(Enum):
    TARAPACA = "I Región de Tarapaca"
    ANTOFAGASTA = "II Región de Antofagasta"
    ATACAMA = "III Región de Atacama"
    COQUIMBO = "IV Región de Coquimbo"
    VALPARAISO = "V Región de Valparaíso"
    LIBERTADOR_O_HIGGINS = "VI Región del Libertador Gral. Bernardo O Higgins"
    MAULE = "VII Región del Maule"
    BIO_BIO = "VIII Región del Bio Bio"
    ARAUCANIA = "IX Región de la Araucanía"
    LOS_LAGOS = "X Región de los Lagos"
    AYSEN = "XI Región Aysén del Gral. Carlos Ibañes del Campo"
    MAGALLANES_ANTARTICA = "XII Región de Magallanes y de la Antártica Chilena"
    METROPOLITANA = "Región Metropolitana de Santiago"
    LOS_RIOS = "XIV Región de los Ríos"
    ARICA_PARINACOTA = "XV Región de Arica y Parinacota"

    def get_court_label(self) -> str:
        if self == PJUDRegion.METROPOLITANA:
            return "C.A. de Santiago"
        if self == PJUDRegion.TARAPACA:
            return "C.A. de Iquique"
        if self == PJUDRegion.ANTOFAGASTA:
            return "C.A. de Antofagasta"
        if self == PJUDRegion.ATACAMA:
            return "C.A. de Copiapó"
        if self == PJUDRegion.COQUIMBO:
            return "C.A. de Serena"
        if self == PJUDRegion.VALPARAISO:
            return "C.A. de Valparaíso"
        if self == PJUDRegion.LIBERTADOR_O_HIGGINS:
            return "C.A. de Rancagua"
        if self == PJUDRegion.MAULE:
            return "C.A. de Talca"
        if self == PJUDRegion.BIO_BIO:
            return "C.A. de Concepción"
        if self == PJUDRegion.ARAUCANIA:
            return "C.A. de Temuco"
        if self == PJUDRegion.LOS_LAGOS:
            return "C.A. de Puerto Montt"
        if self == PJUDRegion.AYSEN:
            return "C.A. de Coyhaique"
        if self == PJUDRegion.MAGALLANES_ANTARTICA:
            return "C.A. de Punta Arenas"
        if self == PJUDRegion.LOS_RIOS:
            return "C.A. de Valdivia"
        if self == PJUDRegion.ARICA_PARINACOTA:
            return "C.A. de Arica"
        return "C.A. de Santiago"
    
    def get_commune_enum(self) -> PJUDCommune:
        if self == PJUDRegion.METROPOLITANA:
            return PJUDCommuneMetropolitana
        if self == PJUDRegion.TARAPACA:
            return PJUDCommuneTarapaca
        if self == PJUDRegion.ANTOFAGASTA:
            return PJUDCommuneAntofagasta
        if self == PJUDRegion.ATACAMA:
            return PJUDCommuneAtacama
        if self == PJUDRegion.COQUIMBO:
            return PJUDCommuneCoquimbo
        if self == PJUDRegion.VALPARAISO:
            return PJUDCommuneValparaiso
        if self == PJUDRegion.LIBERTADOR_O_HIGGINS:
            return PJUDCommuneLibertadorOHiggins
        if self == PJUDRegion.MAULE:
            return PJUDCommuneMaule
        if self == PJUDRegion.BIO_BIO:
            return PJUDCommuneBioBio
        if self == PJUDRegion.ARAUCANIA:
            return PJUDCommuneAraucania
        if self == PJUDRegion.LOS_LAGOS:
            return PJUDCommuneLosLagos
        if self == PJUDRegion.AYSEN:
            return PJUDCommuneAysen
        if self == PJUDRegion.MAGALLANES_ANTARTICA:
            return PJUDCommuneMagallanesAntartica
        if self == PJUDRegion.LOS_RIOS:
            return PJUDCommuneLosRios
        if self == PJUDRegion.ARICA_PARINACOTA:
            return PJUDCommuneAricaParinacota
        raise ValueError("Region not supported")

    def get_tribunal_label(self) -> str:
        if self == PJUDRegion.METROPOLITANA:
            return "Dist. Corte Santiago"
        if self == PJUDRegion.TARAPACA:
            return "Dist. Corte Iquique"
        if self == PJUDRegion.ANTOFAGASTA:
            return "Dist. Corte Antofagasta"
        if self == PJUDRegion.ATACAMA:
            return "Dist. Corte Copiapó"
        if self == PJUDRegion.COQUIMBO:
            return "Dist. Corte La Serena"
        if self == PJUDRegion.VALPARAISO:
            return "Dist. Corte Valparaíso"
        if self == PJUDRegion.LIBERTADOR_O_HIGGINS:
            return "Dist. Corte Rancagua"
        if self == PJUDRegion.MAULE:
            return "Dist. Corte Talca"
        if self == PJUDRegion.BIO_BIO:
            return "Dist. Corte Concepción"
        if self == PJUDRegion.ARAUCANIA:
            return "Dist. Corte Temuco"
        if self == PJUDRegion.LOS_LAGOS:
            return "Dist. Corte Puerto Montt"
        if self == PJUDRegion.AYSEN:
            return "1º Juzgado de Letras de Coyhaique"
        if self == PJUDRegion.MAGALLANES_ANTARTICA:
            return "Dist. Corte Pta. Arenas"
        if self == PJUDRegion.LOS_RIOS:
            return "Dist. Corte Valdivia"
        if self == PJUDRegion.ARICA_PARINACOTA:
            return "Dist. Corte Arica"
        return "Dist. Corte Santiago"


class PJUDCommuneTarapaca(PJUDCommune):
    ALTO_HOSPICIO = "ALTO HOSPICIO"
    CAMINA = "CAMINA"
    COLCHANE = "COLCHANE"
    HUARA = "HUARA"
    IQUIQUE = "IQUIQUE"
    PICA = "PICA"
    POZO_ALMONTE = "POZO ALMONTE"


class PJUDCommuneAntofagasta(PJUDCommune):
    ANTOFAGASTA = "ANTOFAGASTA"
    CALAMA = "CALAMA"
    MARIA_ELENA = "MARIA ELENA"
    MEJILLONES = "MEJILLONES"
    OLLAGUE = "OLLAGUE"
    SAN_PEDRO_DE_ATACAMA = "SAN PEDRO DE ATACAMA"
    SIERRA_GORDA = "SIERRA GORDA"
    TALTAL = "TALTAL"
    TOCOPILLA = "TOCOPILLA"


class PJUDCommuneAtacama(PJUDCommune):
    ALTO_DEL_CARMEN = "ALTO DEL CARMEN"
    CALDERA = "CALDERA"
    CHANARAL = "CHANARAL"
    COPIAPO = "COPIAPO"
    DIEGO_DE_ALMAGRO = "DIEGO DE ALMAGRO"
    FREIRINA = "FREIRINA"
    HUASCO = "HUASCO"
    TIERRA_AMARILLA = "TIERRA AMARILLA"
    VALLENAR = "VALLENAR"


class PJUDCommuneCoquimbo(PJUDCommune):
    ANDACOLLO = "ANDACOLLO"
    CANELA = "CANELA"
    COMBARBALA = "COMBARBALA"
    COQUIMBO = "COQUIMBO"
    ILLAPEL = "ILLAPEL"
    LA_HIGUERA = "LA HIGUERA"
    LA_SERENA = "LA SERENA"
    LOS_VILOS = "LOS VILOS"
    MONTE_PATRIA = "MONTE PATRIA"
    OVALLE = "OVALLE"
    PAIGUANO = "PAIGUANO"
    PUNITAQUI = "PUNITAQUI"
    RIO_HURTADO = "RIO HURTADO"
    SALAMANCA = "SALAMANCA"
    VICUNA = "VICUNA"


class PJUDCommuneValparaiso(PJUDCommune):
    ALGARROBO = "ALGARROBO"
    CABILDO = "CABILDO"
    CALLE_LARGA = "CALLE LARGA"
    CARTAGENA = "CARTAGENA"
    CASABLANCA = "CASABLANCA"
    CATEMU = "CATEMU"
    CONCON = "CONCON"
    EL_QUISCO = "EL QUISCO"
    EL_TABO = "EL TABO"
    HIJUELAS = "HIJUELAS"
    ISLA_DE_PASCUA = "ISLA DE PASCUA"
    JUAN_FERNANDEZ = "JUAN FERNANDEZ"
    LA_CALERA = "LA CALERA"
    LA_CRUZ = "LA CRUZ"
    LA_LIGUA = "LA LIGUA"
    LIMACHE = "LIMACHE"
    LLAILLAY = "LLAILLAY"
    LOS_ANDES = "LOS ANDES"
    NOGALES = "NOGALES"
    OLMUE = "OLMUE"
    PANQUEHUE = "PANQUEHUE"
    PAPUDO = "PAPUDO"
    PETORCA = "PETORCA"
    PUCHUNCAVI = "PUCHUNCAVI"
    PUTAENDO = "PUTAENDO"
    QUILLOTA = "QUILLOTA"
    QUILPUE = "QUILPUE"
    QUINTERO = "QUINTERO"
    RINCONADA = "RINCONADA"
    SAN_ANTONIO = "SAN ANTONIO"
    SAN_ESTEBAN = "SAN ESTEBAN"
    SAN_FELIPE = "SAN FELIPE"
    SANTA_MARIA = "SANTA MARIA"
    SANTO_DOMINGO = "SANTO DOMINGO"
    VALPARAISO = "VALPARAISO"
    VILLA_ALEMANA = "VILLA ALEMANA"
    VINA_DEL_MAR = "VINA DEL MAR"
    ZAPALLAR = "ZAPALLAR"


class PJUDCommuneLibertadorOHiggins(PJUDCommune):
    CHEPICA = "CHEPICA"
    CHIMBARONGO = "CHIMBARONGO"
    CODEGUA = "CODEGUA"
    COINCO = "COINCO"
    COLTAUCO = "COLTAUCO"
    DONIHUE = "DONIHUE"
    GRANEROS = "GRANEROS"
    LA_ESTRELLA = "LA ESTRELLA"
    LAS_CABRAS = "LAS CABRAS"
    LITUECHE = "LITUECHE"
    LOLOL = "LOLOL"
    MACHALI = "MACHALI"
    MALLOA = "MALLOA"
    MARCHIGUE = "MARCHIGUE"
    MOSTAZAL = "MOSTAZAL"
    NANCAGUA = "NANCAGUA"
    NAVIDAD = "NAVIDAD"
    OLIVAR = "OLIVAR"
    PALMILLA = "PALMILLA"
    PAREDONES = "PAREDONES"
    PERALILLO = "PERALILLO"
    PEUMO = "PEUMO"
    PICHIDEGUA = "PICHIDEGUA"
    PICHILEMU = "PICHILEMU"
    PLACILLA = "PLACILLA"
    PUMANQUE = "PUMANQUE"
    QUINTA_DE_TILCOCO = "QUINTA DE TILCOCO"
    RANCAGUA = "RANCAGUA"
    RENGO = "RENGO"
    REQUINOA = "REQUINOA"
    SAN_FERNANDO = "SAN FERNANDO"
    SAN_VICENTE = "SAN VICENTE"
    SANTA_CRUZ = "SANTA CRUZ"


class PJUDCommuneMaule(PJUDCommune):
    CAUQUENES = "CAUQUENES"
    CHANCO = "CHANCO"
    COLBUN = "COLBUN"
    CONSTITUCION = "CONSTITUCION"
    CUREPTO = "CUREPTO"
    CURICO = "CURICO"
    EMPEDRADO = "EMPEDRADO"
    HUALANE = "HUALANE"
    LICANTEN = "LICANTEN"
    LINARES = "LINARES"
    LONGAVI = "LONGAVI"
    MAULE = "MAULE"
    MOLINA = "MOLINA"
    PARRAL = "PARRAL"
    PELARCO = "PELARCO"
    PELLUHUE = "PELLUHUE"
    PENCAHUE = "PENCAHUE"
    RAUCO = "RAUCO"
    RETIRO = "RETIRO"
    RIO_CLARO = "RIO CLARO"
    ROMERAL = "ROMERAL"
    SAGRADA_FAMILIA = "SAGRADA FAMILIA"
    SAN_CLEMENTE = "SAN CLEMENTE"
    SAN_JAVIER = "SAN JAVIER"
    SAN_RAFAEL = "SAN RAFAEL"
    TALCA = "TALCA"
    TENO = "TENO"
    VICHUQUEN = "VICHUQUEN"
    VILLA_ALEGRE = "VILLA ALEGRE"
    YERBAS_BUENAS = "YERBAS BUENAS"


class PJUDCommuneBioBio(PJUDCommune):
    ALTO_BIO_BIO = "ALTO BIO BIO"
    ANTUCO = "ANTUCO"
    ARAUCO = "ARAUCO"
    BULNES = "BULNES"
    CABRERO = "CABRERO"
    CANETE = "CANETE"
    CHIGUAYANTE = "CHIGUAYANTE"
    CHILLAN = "CHILLAN"
    CHILLAN_VIEJO = "CHILLAN VIEJO"
    COBQUECURA = "COBQUECURA"
    COELEMU = "COELEMU"
    COIHUECO = "COIHUECO"
    CONCEPCION = "CONCEPCION"
    CONTULMO = "CONTULMO"
    CORONEL = "CORONEL"
    CURANILAHUE = "CURANILAHUE"
    EL_CARMEN = "EL CARMEN"
    FLORIDA = "FLORIDA"
    HUALPEN = "HUALPEN"
    HUALQUI = "HUALQUI"
    LAJA = "LAJA"
    LEBU = "LEBU"
    LOS_ALAMOS = "LOS ALAMOS"
    LOS_ANGELES = "LOS ANGELES"
    LOTA = "LOTA"
    MULCHEN = "MULCHEN"
    NACIMIENTO = "NACIMIENTO"
    NEGRETE = "NEGRETE"
    NINHUE = "NINHUE"
    NIQUEN = "NIQUEN"
    PEMUCO = "PEMUCO"
    PENCO = "PENCO"
    PINTO = "PINTO"
    PORTEZUELO = "PORTEZUELO"
    QUILACO = "QUILACO"
    QUILLECO = "QUILLECO"
    QUILLON = "QUILLON"
    QUIRIHUE = "QUIRIHUE"
    RANQUIL = "RANQUIL"
    SAN_CARLOS = "SAN CARLOS"
    SAN_FABIAN = "SAN FABIAN"
    SAN_IGNACIO = "SAN IGNACIO"
    SAN_NICOLAS = "SAN NICOLAS"
    SAN_PEDRO_DE_LA_PAZ = "SAN PEDRO DE LA PAZ"
    SAN_ROSENDO = "SAN ROSENDO"
    SANTA_BARBARA = "SANTA BARBARA"
    SANTA_JUANA = "SANTA JUANA"
    TALCAHUANO = "TALCAHUANO"
    TIRUA = "TIRUA"
    TOME = "TOME"
    TREGUACO = "TREGUACO"
    TUCAPEL = "TUCAPEL"
    YUMBEL = "YUMBEL"
    YUNGAY = "YUNGAY"


class PJUDCommuneAraucania(PJUDCommune):
    ANGOL = "ANGOL"
    CARAHUE = "CARAHUE"
    CHOLCHOL = "CHOLCHOL"
    COLLIPULLI = "COLLIPULLI"
    CUNCO = "CUNCO"
    CURACAUTIN = "CURACAUTIN"
    CURARREHUE = "CURARREHUE"
    ERCILLA = "ERCILLA"
    FREIRE = "FREIRE"
    GALVARINO = "GALVARINO"
    GORBEA = "GORBEA"
    LAUTARO = "LAUTARO"
    LONCOCHE = "LONCOCHE"
    LONQUIMAY = "LONQUIMAY"
    LOS_SAUCES = "LOS SAUCES"
    LUMACO = "LUMACO"
    MELIPEUCO = "MELIPEUCO"
    NUEVA_IMPERIAL = "NUEVA IMPERIAL"
    PADRE_LAS_CASAS = "PADRE LAS CASAS"
    PERQUENCO = "PERQUENCO"
    PITRUFQUEN = "PITRUFQUEN"
    PUCON = "PUCON"
    PUREN = "PUREN"
    RENAICO = "RENAICO"
    SAAVEDRA = "SAAVEDRA"
    TEMUCO = "TEMUCO"
    TEODORO_SCHMIDT = "TEODORO SCHMIDT"
    TOLTEN = "TOLTEN"
    TRAIGUEN = "TRAIGUEN"
    VICTORIA = "VICTORIA"
    VILCUN = "VILCUN"
    VILLARRICA = "VILLARRICA"


class PJUDCommuneLosLagos(PJUDCommune):
    ANCUD = "ANCUD"
    CALBUCO = "CALBUCO"
    CASTRO = "CASTRO"
    CHAITEN = "CHAITEN"
    CHONCHI = "CHONCHI"
    COCHAMO = "COCHAMO"
    CURACO_DE_VELEZ = "CURACO DE VELEZ"
    DALCAHUE = "DALCAHUE"
    FRESIA = "FRESIA"
    FRUTILLAR = "FRUTILLAR"
    FUTALEFU = "FUTALEFU"
    HUALAIHUE = "HUALAIHUE"
    LLANQUIHUE = "LLANQUIHUE"
    LOS_MUERMOS = "LOS MUERMOS"
    MAULLIN = "MAULLIN"
    OSORNO = "OSORNO"
    PALENA = "PALENA"
    PUERTO_MONTT = "PUERTO MONTT"
    PUERTO_OCTAY = "PUERTO OCTAY"
    PUERTO_VARAS = "PUERTO VARAS"
    PUQUELDON = "PUQUELDON"
    PURRANQUE = "PURRANQUE"
    PUYEHUE = "PUYEHUE"
    QUEILEN = "QUEILEN"
    QUELLON = "QUELLON"
    QUEMCHI = "QUEMCHI"
    QUINCHAO = "QUINCHAO"
    RIO_NEGRO = "RIO NEGRO"
    SAN_JUAN_DE_LA_COSTA = "SAN JUAN DE LA COSTA"
    SAN_PABLO = "SAN PABLO"


class PJUDCommuneAysen(PJUDCommune):
    AYSEN = "AYSEN"
    CHILE_CHICO = "CHILE CHICO"
    CISNES = "CISNES"
    COCHRANE = "COCHRANE"
    COYHAIQUE = "COYHAIQUE"
    GUAITECAS = "GUAITECAS"
    LAGO_VERDE = "LAGO VERDE"
    RIO_IBANEZ = "RIO IBANEZ"
    TORTEL = "TORTEL"
    VILLA_OHIGGINS = "VILLA OHIGGINS"


class PJUDCommuneMagallanesAntartica(PJUDCommune):
    CABO_DE_HORNOS = "CABO DE HORNOS"
    LAGUNA_BLANCA = "LAGUNA BLANCA"
    NATALES = "NATALES"
    PORVENIR = "PORVENIR"
    PRIMAVERA = "PRIMAVERA"
    PUNTA_ARENAS = "PUNTA ARENAS"
    RIO_VERDE = "RIO VERDE"
    SAN_GREGORIO = "SAN GREGORIO"
    TIMAUKEL = "TIMAUKEL"
    TORRES_DEL_PAINE = "TORRES DEL PAINE"


class PJUDCommuneMetropolitana(PJUDCommune):
    ALHUE = "ALHUE"
    BUIN = "BUIN"
    CALERA_DE_TANGO = "CALERA DE TANGO"
    CERRILLOS = "CERRILLOS"
    CERRO_NAVIA = "CERRO NAVIA"
    COLINA = "COLINA"
    CONCHALI = "CONCHALI"
    CURACAVI = "CURACAVI"
    EL_BOSQUE = "EL BOSQUE"
    EL_MONTE = "EL MONTE"
    ESTACION_CENTRAL = "ESTACION CENTRAL"
    HUECHURABA = "HUECHURABA"
    INDEPENDENCIA = "INDEPENDENCIA"
    ISLA_DE_MAIPO = "ISLA DE MAIPO"
    LA_CISTERNA = "LA CISTERNA"
    LA_FLORIDA = "LA FLORIDA"
    LA_GRANJA = "LA GRANJA"
    LA_PINTANA = "LA PINTANA"
    LA_REINA = "LA REINA"
    LAMPA = "LAMPA"
    LAS_CONDES = "LAS CONDES"
    LO_BARNECHEA = "LO BARNECHEA"
    LO_ESPEJO = "LO ESPEJO"
    LO_PRADO = "LO PRADO"
    MACUL = "MACUL"
    MAIPU = "MAIPU"
    MARIA_PINTO = "MARIA PINTO"
    MELIPILLA = "MELIPILLA"
    NUNOA = "NUNOA"
    PADRE_HURTADO = "PADRE HURTADO"
    PAINE = "PAINE"
    PEDRO_AGUIRRE_CERDA = "PEDRO AGUIRRE CERDA"
    PENAFLOR = "PENAFLOR"
    PENALOLEN = "PENALOLEN"
    PIRQUE = "PIRQUE"
    PROVIDENCIA = "PROVIDENCIA"
    PUDAHUEL = "PUDAHUEL"
    PUENTE_ALTO = "PUENTE ALTO"
    QUILICURA = "QUILICURA"
    QUINTA_NORMAL = "QUINTA NORMAL"
    RECOLETA = "RECOLETA"
    RENCA = "RENCA"
    SAN_BERNARDO = "SAN BERNARDO"
    SAN_JOAQUIN = "SAN JOAQUIN"
    SAN_JOSE_DE_MAIPO = "SAN JOSE DE MAIPO"
    SAN_MIGUEL = "SAN MIGUEL"
    SAN_PEDRO = "SAN PEDRO"
    SAN_RAMON = "SAN RAMON"
    SANTIAGO = "SANTIAGO"
    TALAGANTE = "TALAGANTE"
    TIL_TIL = "TIL TIL"
    VITACURA = "VITACURA"


class PJUDCommuneLosRios(PJUDCommune):
    CORRAL = "CORRAL"
    FUTRONO = "FUTRONO"
    LA_UNION = "LA UNION"
    LAGO_RANCO = "LAGO RANCO"
    LANCO = "LANCO"
    LOS_LAGOS = "LOS LAGOS"
    MAFIL = "MAFIL"
    MARIQUINA = "MARIQUINA"
    PAILLACO = "PAILLACO"
    PANGUIPULLI = "PANGUIPULLI"
    RIO_BUENO = "RIO BUENO"
    VALDIVIA = "VALDIVIA"


class PJUDCommuneAricaParinacota(PJUDCommune):
    ARICA = "ARICA"
    CAMARONES = "CAMARONES"
    GENERAL_LAGOS = "GENERAL LAGOS"
    PUTRE = "PUTRE"


class PJUDAddressType(str, Enum):
    PRIVATE = "private"
    COMMERCIAL = "commercial"


class PJUDStreetType(str, Enum):
    AVENUE = "avenue"
    STREET = "street"
    ALLEYWAY = "alleyway"


class PJUDAddress(BaseModel):
    address_type: PJUDAddressType = Field(PJUDAddressType.COMMERCIAL, description="Type of address")
    street_type: PJUDStreetType = Field(PJUDStreetType.STREET, description="Type of street")
    address: str = Field(..., description="Address name")
    address_number: str = Field(..., description="Address number")
    commune: PJUDCommune = Field(PJUDCommuneMetropolitana.SANTIAGO, description="Adress commune")
    region: PJUDRegion = Field(PJUDRegion.METROPOLITANA, description="Adress region")

    @model_validator(mode="before")
    def convert_commune(cls, values):
        region_value = values.get("region")
        if isinstance(region_value, str):
            region_enum = next((region for region in PJUDRegion if region.value == region_value), None)
            if region_enum is None:
                raise ValueError(f"Invalid region value: {region_value}")
            values["region"] = region_enum
        commune_value = values.get("commune")
        if isinstance(commune_value, str) and "region" in values:
            try:
                commune_enum = values["region"].get_commune_enum()
                commune_enum_value = next((commune for commune in commune_enum if commune.value == commune_value), None)
            except KeyError:
                raise ValueError(f"Invalid commune value: {commune_value} for region: {values['region']}")
            values["commune"] = commune_enum_value
        return values

    def get_adress_type_label(self) -> str:
        if self.address_type == PJUDAddressType.COMMERCIAL:
            return "Comercial"
        return "Particular"
    
    def get_street_type_label(self) -> str:
        if self.street_type == PJUDStreetType.AVENUE:
            return "Avenida"
        if self.street_type == PJUDStreetType.ALLEYWAY:
            return "Psje"
        return "Calle"
    

class PJUDLegalRepresentative(BaseModel):
    raw_name: str = Field(..., description="Raw name of the legal representative")
    identifier: str = Field(..., description="RUT of the legal representative")


class PJUDDDO(BaseModel):
    raw_address: str = Field(..., description="Raw main address of the DDO. entity")
    raw_name: str = Field(..., description="Raw name of the DDO. entity")
    identifier: str = Field(..., description="RUT of the DDO. entity")
    legal_representatives: list[PJUDLegalRepresentative] = Field(default_factory=list, description="Legal representatives of the DDO. entity, if any")
    addresses: list[PJUDAddress] = Field(..., description="DDO. entity addresses")
