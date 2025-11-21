export const exampleData = [
    {
        name: "FELIPE FERNANDO PIZARRO CORRAL",
        rut: "66470563",
        type: "PERSONA",
        bienes: [
            {
                source: "Conservadores Digitales",
                url: "https://conservadoresdigitales.cl/conservador/santiago/consultas-en-linea/indice-de-propiedad",
                headers: ["Foja", "Número", "Año", "Dirección"],
                values: [
                    ["28278", "37594", "1981", "Calle A 1950"],
                    ["2284", "1556", "1998", "Pablo Burchard 1940"],
                ],
            },
              {
                source: "deQuiénes",
                url: "https://dequienes.cl/",
                headers: ["Empresa", "RUT", "Socio"],
                values: [
                    ["BERZINS Y PIZARRO LIMITADA", "77.437.070-6", "Sí"],
                    ["COMERCIAL PIZARRO Y COMPANIA LIMITADA", "77.031.800-9", "Sí"],
                    ["COMERCIAL TRANSAMERICA LIMITADA", "77.406.150-9", "Sí"],
                    ["SOC COMERCIAL PROSPER STORES LIMITADA", "77.809.230-1", "Sí"],
                    ["SOCIEDAD DE INVERSIONES PIZARRO E HIJOS S.A", "77.809.030-9", "Sí"],
                ],
            },
            {
                source: "CMF",
                url: "https://www.cmfchile.cl/",
                headers: ["Razón Social", "RUT", "Acciones (%)"],
                values: [
                    ["LIGA INDEPENDIENTE DE FUTBOL S.A.", "94.514.000-3", "<1"],
                ]
            }
        ],
    },
    {
        name: "VIA UNO CHILE SPA",
        rut: "76055749-8",
        type: "EMPRESA",
        bienes: [
            {
                source: "Volante o Maleta",
                sources: [
                    { source: "Registro de vehículos motorizados", url: "https://www.registrosciviles.cl/tramites/registro-de-vehiculos-motorizados/" },
                    { source: "Volante o Maleta", url: "https://www.volanteomaleta.com/" },
                ],
                url: "https://www.volanteomaleta.com/",
                headers: ["Patente", "Tipo", "Marca", "Modelo", "Nro. Motor", "Año", "Nombre a Rutificador"],
                values: [
                    ["KRKG72", "Camion", "Chevrolet", "NQR 919", "4HK1681283", "2018", "Via Uno Chile Spa"],
                ],
            },
        ],
    },
    {
        name: "RENE PIANTINI CASTILLO", 
        rut: "53094023",
        type: "PERSONA",
        bienes: [
            {
                source: "Conservador de Bienes Raíces",
                url: "https://conservadoresdigitales.cl/conservador/santiago/consultas-en-linea/indice-de-propiedad",
                headers: ["Foja", "Número", "Año", "Dirección"],
                values: [
                    ["41704", "40213", "2005", "Roger de Flor 2900 Departamento 23, Estacionamiento 43 y Bodega 38"],
                    ["6418", "5351", "1988", "Nueva York 53 Of. 54"],
                    ["55716", "80879", "2019", "Callao 3366 Depto. 74 Bg. 59 Estac. 32"],
                    ["63368", "92077", "2019", "San Carlos 2985 Depto. 131, Estac. 025 Y Bg. 10"],
                    ["36241", "28370", "1993", "Las Perdices 275"]
                ]
            },
            {
                source: "deQuiénes",
                url: "https://dequienes.cl/",
                headers: ["Empresa", "RUT", "Socio"],
                values: [
                    ["PRODALMAR II S.A.", "76.412.702-1", "Sí"],
                    ["GEICOS S.A.", "99.561.480-4", "Sí"],
                    ["CONSTRUCTORA E INMOBILIARIA PIANTINI S.A.", "96.656.800-0", "Sí"],
                    ["INMOBILIARIA LIDIA SPA", "77.057.044-1", "Sí"],
                    ["SERVICIOS GASTRONOMICOS PIAMONTE LIMITADA", "76.016.538-7", "Sí"],
                    ["INMOBILIARIA E INVERSIONES PIACENZA S.A.", "76.448.800-7", "Sí"],
                    ["INVERSIONES KELP S.A.", "99.557.500-5", "Sí"],
                    ["VIÑEDOS LAGAR DE CODEGUA SPA", "76.768.784-2", "Sí"]
                ]
            },
            {
                source: "CMF",
                url: "https://www.cmfchile.cl/portal/principal/613/w3-channel.html",
                headers: ["Razón Social", "RUT", "Acciones (%)"],
                values: [
                    ["COMPAÑÍA GENERAL DE ELECTRICIDAD S.A.", "76.411.321-7", ">20%"],
                    ["EMPRESA ELÉCTRICA DE ARICA S.A.", "96.542.120-3", "10%-20%"],
                    ["EMPRESA ELÉCTRICA DE IQUIQUE S.A.", "96.541.870-9", "5%-10%"],
                    ["INVERSIONES ORO LTDA.", "96.611.120-8", "1%-5%"]
                ]
            },
            {
                source: "Volante o Maleta + Registro de Vehículos Motorizados",
                sources: [
                    { source: "Volante o Maleta", url: "https://www.volanteomaleta.com/" },
                    { source: "Registro de vehículos motorizados", url: "https://www.registrosciviles.cl/tramites/registro-de-vehiculos-motorizados/" }
                ],
                url: "https://www.volanteomaleta.com/",
                headers: ["Patente", "Tipo", "Marca", "Modelo", "Nro. Motor", "Año", "Nombre a Rutificador"],
                values:  [
                    ["AB3154", "Automovil", "Bmw", "518", "184VC7444648", "1981", "Piantini Castillo Rene Humberto"],
                    ["EG0579", "Motocicleta", "Honda", "Trx 200", "A9E2979", "1990", "Piantini Castillo Rene Humberto"],
                    ["DI4856", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "1991", "Piantini Castillo Rene Humberto"],
                    ["EE0669", "Motocicleta", "Honda", "Trx 200", "8201115", "1992", "Piantini Castillo Rene Humberto"],
                    ["KP1883", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "1993", "Piantini Castillo Rene Humberto"],
                    ["DI4857", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "1991", "Piantini Castillo Rene Humberto"]
                ]
            }
        ]
    },
    {
        name: "PRODUCTORA DE ALGAS MARINAS S.A.",
        rut: "784386600",
        type: "EMPRESA",
        bienes: [
            {
                source: "Conservador de Bienes Raíces",
                url: "https://conservadoresdigitales.cl/conservador/santiago/consultas-en-linea/indice-de-propiedad",
                headers: ["Foja", "Número", "Año", "Dirección"],
                values: [
                    ["44130", "63053", "2016", "Avenida Apoquindo 2930 Estac. 3018, 3019, 4001, 4002, 4017, Bg. 4.04"],
                ]
            },
            {
                source: "Volante o Maleta + Registro de Vehículos Motorizados",
                sources: [
                    { source: "Volante o Maleta", url: "https://www.volanteomaleta.com/" },
                    { source: "Registro de vehículos motorizados", url: "https://www.registrosciviles.cl/tramites/registro-de-vehiculos-motorizados/" }
                ],
                headers: ["Patente", "Tipo", "Marca", "Modelo", "Nro. Motor", "Año", "Nombre a Rutificador"],
                values: [
                    ["FTTF74", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2013", "Productora De Algas Marinas Ltda"],
                    ["PG6459", "Camioneta", "Nissan", "Pick Up 2.4 Dx", "KA24158976R", "1996", "Productora De Algas Marinas Ltda"],
                    ["YL6535", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2005", "Productora De Algas Marinas Ltda"],
                    ["FB7316", "Furgon", "Fiat", "Fiorino", "2623610", "1988", "Productora De Algas Marinas Ltda"],
                    ["SD5303", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "1998", "Productora De Algas Marinas Ltda"],
                    ["SY6813", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "1998", "Productora De Algas Marinas Ltda"],
                    ["UL8245", "Camioneta", "Hyundai", "Porter Au D Cab 2.6", "D4BB1070021", "2001", "Productora De Algas Marinas Ltda"],
                    ["GD7614", "Camioneta", "Chevrolet", "C 10", "M0518TBU31498", "1977", "Productora De Algas Marinas Ltda"],
                    ["VN9108", "Camioneta", "Tata", "Telcoine D Cab 1.9", "GYZ715764", "2002", "Productora De Algas Marinas Ltda"],
                    ["DB4876", "Camioneta", "Nissan", "Pick Up 1800 Doble Cabin", "M8Z0D0028", "1990", "Productora De Algas Marinas Ltda"],
                    ["BXBV61", "Furgon", "Peugeot", "Partner M59 Hdi 1.6", "10JBAW0070286", "2009", "Productora De Algas Marinas Ltda"],
                    ["CBXT31", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2008", "Productora De Algas Marinas Ltda"],
                    ["FDSY35", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2013", "Productora De Algas Marinas Ltda"],
                    ["DRGY73", "Camioneta", "Ford", "Ranger Xlt 4x4 2.5", "WLAT1314335", "2012", "Productora De Algas Marinas Ltda"],
                    ["FDSY34", "Bus", "Jac", "City Advantage Hk6750k", "89061294", "2013", "Productora De Algas Marinas Ltda"],
                    ["BZBZ97", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2010", "Productora De Algas Marinas Ltda"]
                ]
            }
              
        ]
    },
    {
        name: "ALFONSO FUENZALIDA CALVO",
        rut: "63724238",
        type: "PERSONA",
        bienes: [
            {
                source: "Conservador de Bienes Raíces",
                url: "https://conservadoresdigitales.cl/conservador/santiago/consultas-en-linea/indice-de-propiedad",
                headers: ["Foja", "Número", "Año", "Dirección"],
                values: [
                    ["38063", "53546", "2020", "Paseo de Alcala 11286"],
                    ["37961", "53407", "2020", "Emille Allais S/n, Depto.201, Est. E-7, Bg. B-7"],
                    ["37908", "53336", "2020", "Roger de Flor 2871 Ofician 202, Box 22"]
                ]
            },
            {
                source: "deQuiénes",
                url: "https://dequienes.cl/",
                headers: ["Empresa", "RUT", "Socio"],
                values: [
                    ["AGRICOLA Y FORESTAL VICHUQUEN LIMITADA", "76.183.345-6", "Sí"],
                    ["ADMINISTRADORA PETROHUE LIMITADA", "76.318.965-1", "Sí"],
                    ["ARRENDOS PUCON S.A.", "76.327.619-8", "Sí"],
                    ["CONSTRUCTORA ROMA SPA", "76.756.749-9", "Sí"],
                    ["COURT ASESORIAS INMOBILIARIAS S.A.", "76.121.021-1", "Sí"],
                    ["FONDO DE INVERSION PRIVADO PETROHUE", "76.254.895-K", "Sí"],
                    ["FONDO DE INVERSION PRIVADO PUCON", "76.306.838-2", "Sí"],
                    ["INMOBILIARIA DIRECTOR MANQUEHUE SPA", "76.934.069-6", "Sí"],
                    ["INMOBILIARIA DIRECTOR MANQUEHUE SPA", "77.029.106-2", "Sí"],
                    ["INMOBILIARIA LA POSA S.A.", "76.350.094-2", "Sí"],
                    ["INMOBILIARIA SANTA JULIA S.A", "76.351.530-3", "Sí"],
                    ["INMOBILIARIA SANTA MARIA SPA", "76.117.044-9", "Sí"],
                    ["INMOBILIARIA Y GESTORA IKA LIMITADA", "76.415.266-2", "Sí"],
                    ["INMOBILIARIA TRIGALES S.A.", "76.411.313-6", "Sí"],
                    ["INVERSIONES COURT LIMITADA", "76.058.248-4", "Sí"],
                    ["INVERSIONES DON PATRICIO S.A.", "76.418.904-3", "Sí"],
                    ["INVERSIONES FLORENCIA SPA", "76.763.513-3", "Sí"],
                    ["INVERSIONES LOS PEUMOS DOS LIMITADA", "76.090.005-2", "Sí"],
                    ["INVERSIONES LOS PEUMOS LIMITADA", "76.388.380-9", "Sí"],
                    ["INVERSIONES PETROHUE II LIMITADA", "76.414.973-4", "Sí"],
                    ["INVERSIONES PETROHUE LIMITADA", "87.785.900-2", "Sí"],
                    ["INVERSIONES SURANCE LIMITADA", "76.255.839-4", "Sí"],
                    ["PETROHUE LAS CONDES S.A.", "76.259.206-1", "Sí"]
                ]
            },
            {
                source: "CMF",
                url: "https://www.cmfchile.cl/portal/principal/613/w3-channel.html",
                headers: ["Razón Social", "RUT", "Acciones (%)"],
                values: [
                    ["INVERSIONES SQYA SPA", "96.979.520-5", ">20%"],
                    ["BTG PACTUAL CHILE S A C DE B", "96.966.250-7", "1%-5%"],
                    ["CREDICORP CAPITAL CORREDORES DE BOLSA SPA", "96.489.000-5", "1%-5%"],
                    ["LARRAIN VIAL S A CORREDORA DE BOLSA", "60.810.000-8", "1%-5%"],
                    ["NEVASA S.A CORREDORES DE BOLSA", "96.586.750-3", "1%-5%"],
                    //["PIONERO FONDO DE INVERSION", "—", "1%-5%"]
                ]
            },
            {
                source: "Volante o Maleta + Registro de Vehículos Motorizados",
                sources: [
                    { source: "Volante o Maleta", url: "https://www.volanteomaleta.com/" },
                    { source: "Registro de vehículos motorizados", url: "https://www.registrosciviles.cl/tramites/registro-de-vehiculos-motorizados/" }
                ],
                url: "https://www.volanteomaleta.com/",
                headers: ["Patente", "Tipo", "Marca", "Modelo", "Nro. Motor", "Año", "Nombre a Rutificador"],
                values: [
                    ["CA0532", "Motocicleta", "Honda", "Sin Datos", "2111878", "1984", "Fuenzalida Calvo Alfonso"]
                ]
            }
              
        ]
    },
    {
        name: "INMOBILIARIA PLAZA PEDRO DE VALDIVIA SpA",
        rut: "77104526K",
        type: "EMPRESA",
        bienes: [
            {
                source: "Conservador de Bienes Raíces",
                url: "https://conservadoresdigitales.cl/conservador/santiago/consultas-en-linea/indice-de-propiedad",
                headers: ["Foja", "Número", "Año", "Dirección"],
                values: [
                    ["12549", "18167", "2022", "Francisco Bilbao 1933"],
                    ["6750", "9697", "2022", "Avenida Francisco Bilbao 1907"],
                    ["9920", "14305", "2022", "Avenida Francisco Bilbao 1939"]
                ]
            },
        ]
    },
    {
        name: "IGNACIO DOMINGO GODOY LÓPEZ",
        rut: "163558602",
        type: "PERSONA",
        bienes: [
            {
                source: "Conservador de Bienes Raíces",
                url: "https://conservadoresdigitales.cl/conservador/santiago/consultas-en-linea/indice-de-propiedad",
                headers: ["Foja", "Número", "Año", "Dirección"],
                values: [
                    ["47341", "68872", "2022", "Cerro Las Bandurrias 12163 St. 31 A-3, Mz. B"]
                ]
            },
            {
                source: "deQuiénes",
                url: "https://dequienes.cl/",
                headers: ["Empresa", "RUT", "Socio"],
                values: [
                    ["INVERSIONES TRES SANTOS SPA", "77.556.056-8", "Sí"],
                    ["INVERSIONES BEIT SAHOUR LIMITADA", "77.556.081-9", "Sí"],
                    ["MAYSER SPA", "76.243.577-2", "Sí"],
                    ["ASESORIAS E INVERSIONES GUHMA SPA", "77.155.082-7", "Sí"],
                    ["BIWO SERVICES S.A.", "77.101.074-1", "Sí"],
                    ["GODOY & MANCILLA INVERSIONES LIMITADA", "76.065.593-7", "Sí"],
                    ["MARIANENSE CHILE SPA", "76.717.365-2", "Sí"],
                    ["CURAPAU SPA", "77.561.974-0", "Sí"],
                    ["INVERSIONES DOS SANTOS SPA", "77.356.882-0", "Sí"],
                    ["BIWO RENOVABLES S.A.", "77.104.666-5", "Sí"],
                    ["COMERCIALIZADORA SANTA FE SA", "76.218.407-9", "Sí"],
                    ["CONSORCIO SANTA FE - P & A S.A.", "76.165.217-6", "Sí"],
                    ["INVERSIONES SANTA FE SOCIEDAD ANONIMA", "99.541.880-0", "Sí"],
                    ["INVERSIONES XALTA SPA", "76.589.991-5", "Sí"],
                    ["INVERSIONES MOBILIARIAS E INMOBILIARIAS SANTA MARIANA S.A.", "76.148.569-5", "Sí"],
                    ["INVERSIONES EL ROBLE S.A.", "77.532.093-1", "Sí"],
                    ["TRUCKTAL SOCIEDAD ANONIMA", "76.148.313-7", "Sí"]
                ]
            },
            {
                source: "CMF",
                url: "https://www.cmfchile.cl/portal/principal/613/w3-channel.html",
                headers: ["Razón Social", "RUT", "Acciones (%)"],
                values: [
                    ["INVERSIONES PREVISIONALES CHILE SPA", "76.438.033-9", ">20%"],
                    ["INVERSIONES PREVISIONALES DOS SA", "76.093.446-1", ">20%"],
                    ["BANCHILE CORREDORES DE BOLSA S A", "96.571.220-8", "1%-5%"],
                    ["BANCO SANTANDER CHILE", "97.036.000-K", "1%-5%"],
                    ["BCI CORREDOR DE BOLSA", "96.519.800-8", "1%-5%"],
                    ["INV UNION ESPAÑOLA S A", "96.513.200-7", "1%-5%"]
                ]
            },
        ]
    },
    {
        name: "DOMINGO GUILLERMO GODOY VÁSQUEZ",
        rut: "68111196",
        type: "PERSONA",
        bienes: [
            {
                source: "Conservador de Bienes Raíces",
                url: "https://conservadoresdigitales.cl/conservador/santiago/consultas-en-linea/indice-de-propiedad",
                headers: ["Foja", "Número", "Año", "Dirección"],
                values: [
                    ["61095", "9462", "2022", "Dinamarca 1897 (Cesion)"],
                    ["50119", "72927", "2022", "Camino El Parque 100 Dep. 302, Bg. B8, Est. E 15, E 16 Edif. Mañio"]
                ]
            },
            {
                source: "deQuiénes",
                url: "https://dequienes.cl/",
                headers: ["Empresa", "RUT", "Socio"],
                values: [
                    ["SOCIEDAD DE INVERSIONES DOS SOLES SPA", "77.241.406-4", "Sí"],
                    ["INVERSIONES EL ROBLE S.A.", "77.532.093-1", "Sí"],
                    ["TRUCKTAL SOCIEDAD ANONIMA", "76.148.313-7", "Sí"],
                    ["INVERSIONES MOBILIARIAS E INMOBILIARIAS SANTA MARIANA S.A.", "76.148.569-5", "Sí"],
                    ["SOC AGRICOLA LOPEZ VACHE LTDA", "78.733.520-9", "Sí"],
                    ["SOCIEDAD DE TRANSPORTE SANTA FE S.A.", "76.035.277-2", "Sí"],
                    ["SANTA FE SERVICIOS PORTUARIOS SOCIEDAD ANONIMA", "76.406.980-3", "Sí"]
                ]
            },
            {
                source: "CMF",
                url: "https://www.cmfchile.cl/portal/principal/613/w3-channel.html",
                headers: ["Razón Social", "RUT", "Acciones (%)"],
                values: [
                    ["CASO Y CIA SAC", "92.423.000-2", ">20%"],
                    ["PRINCIPADO DE ASTURIAS S A", "96.502.770-K", ">20%"],
                    ["BTG PACTUAL CHILE S A C DE B", "96.966.250-7", "1%-5%"],
                    ["CIA DE INVERSIONES LA ESPANOLA SA", "93.727.000-3", "1%-5%"],
                    ["INVERSIONES ALONSO DE ERCILLA SA", "96.502.680-0", "1%-5%"],
                    ["INVERSIONES HISPANIA S A", "99.040.000-8", "1%-5%"],
                    ["INVERSIONES SAN BENITO SA", "96.544.460-2", "1%-5%"]
                ]
            },
        ]
    },
    {
        name: "INGENIERÍA Y CONSTRUCCIONES SANTA FE S.A.",
        rut: "99549106",
        type: "EMPRESA",
        bienes: [
            {
                source: "Conservador de Bienes Raíces",
                url: "https://conservadoresdigitales.cl/conservador/santiago/consultas-en-linea/indice-de-propiedad",
                headers: ["Foja", "Número", "Año", "Dirección"],
                values: [
                    ["26129", "34830", "1981", "Comunidad Guzman Montt Parc. 13 Y 14"],
                    ["46722", "62952", "1980", "Monjitas 557 Al 563"],
                    ["140", "161", "1981", "Miraflores 537"]
                ]
            },
            {
                source: "Volante o Maleta + Registro de Vehículos Motorizados",
                sources: [
                    { source: "Volante o Maleta", url: "https://www.volanteomaleta.com/" },
                    { source: "Registro de vehículos motorizados", url: "https://www.registrosciviles.cl/tramites/registro-de-vehiculos-motorizados/" }
                ],
                url: "https://www.volanteomaleta.com/",
                headers: ["Patente", "Tipo", "Marca", "Modelo", "Nro. Motor", "Año", "Nombre a Rutificador"],
                values: [
                    ["BYCG59", "Sin Datos", "Sin Datos", "HI 740 7", "46844073", "2009", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["BRPL60", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2008", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["GXYJ27", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2015", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["CJGJ26", "Todo Terreno", "Suzuki", "Jimmy Jx Ps 1.3", "M13A2204133", "2010", "Ingeniería Y Construcciones Santa Fe Sociedad Anonima"],
                    ["EH5151", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "1974", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["PG2495", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "1996", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["SL4094", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "1997", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["WB2402", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2006", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["WB2403", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2005", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["ZK5614", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "1992", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["XA2827", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2002", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["YG6862", "Bus", "Volkswagen", "9150 Eod", "30800629", "2005", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["LX9587", "Bus", "Mercedes Benz", "Lo 8124 25", "37495010246410", "1995", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["MZ2040", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2007", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["PT6802", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "1996", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["PU4149", "Bus", "Mitsubishi", "Rosa Bus", "853151", "1997", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["PW7688", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2010", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["JJ4405", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2010", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["SD5038", "Bus", "Mercedes Benz", "Lo 814", "37498410384115", "1998", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["SE9971", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "1998", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["SE9972", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "1998", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["SS1555", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "1991", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["JN9416", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2010", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["YT6995", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2005", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["ZN4138", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2006", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["JA7590", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "1982", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["CWRT39", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2011", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["DCFG90", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2011", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["GHZB19", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2014", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["FYTT18", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2012", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["JSGR13", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2017", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["CYYR12", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2011", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["JFTF94", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2017", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["BRDP40", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2008", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["BKLB44", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2008", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["BRDP41", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2017", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["JFTF95", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2017", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["BLZB47", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2008", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["CFVZ14", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2010", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["CYWG43", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2012", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["GRFS73", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "1986", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["GZYV29", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2015", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["HSHC36", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2016", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["JCKT51", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2015", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["HBPH24", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2005", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["DZSC30", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2012", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["JSTB47", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2017", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["CYSD69", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2006", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["DKHP15", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2011", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["FHJX60", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2013", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["HXDJ32", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2017", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["BSYZ74", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2008", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["DHTB58", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2011", "Ingeniería Y Construcciones Santa Fe S A"],
                    ["JRPR85", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "2017", "Ingeniería Y Construcciones Santa Fe S A"]
                ]
            }
              
        ]
    },
    {
        name: "ANTONIO ZEGERS CORREA",
        rut: "132719098",
        type: "PERSONA",
        bienes: [
            {
                source: "Conservador de Bienes Raíces",
                url: "https://conservadoresdigitales.cl/conservador/santiago/consultas-en-linea/indice-de-propiedad",
                headers: ["Foja", "Número", "Año", "Dirección"],
                values: [
                    ["99020", "103659", "1981", "Estanislao Recabarren 4296"],
                    ["42034", "58889", "1981", "Camino La Capellania 1211"]
                ]
            },
            {
                source: "deQuiénes",
                url: "https://dequienes.cl/",
                headers: ["Empresa", "RUT", "Socio"],
                values: [
                    ["INVERSIONES LAS OVERAS LIMITADA", "77.262.212-0", "Sí"],
                    ["ASESORIAS E INVERSIONES LAFIT LIMITADA", "76.422.610-0", "Sí"],
                    ["NAVARINO CAPITAL PREFERENTE", "76.600.722-8", "Sí"],
                    ["INMOBILIARIA LOS PLATANOS SPA", "77.089.323-2", "Sí"],
                    ["VENTURANCE S.A.", "76.095.786-0", "Sí"],
                    ["GBV CUSTODIO SPA", "77.128.422-1", "Sí"]
                ]
            },
            {
                source: "Volante o Maleta + Registro de Vehículos Motorizados",
                sources: [
                    { source: "Volante o Maleta", url: "https://www.volanteomaleta.com/" },
                    { source: "Registro de vehículos motorizados", url: "https://www.registrosciviles.cl/tramites/registro-de-vehiculos-motorizados/" }
                ],
                url: "https://www.volanteomaleta.com/",
                headers: ["Patente", "Tipo", "Marca", "Modelo", "Nro. Motor", "Año", "Nombre a Rutificador"],
                values: [
                    ["KJTH80", "Camioneta", "Toyota", "Tundra Dcab 5.7 Aut", "3UR6324624", "2018", "Zegers Correa Antonio"],
                    ["FTGL82", "Station Wagon", "Toyota", "4runner 4x4 4.0 Aut", "1GRA713586", "2013", "Zegers Correa Antonio"]
                ]
            }
              
        ]
    },
    {
        name: "INMOBILIARIA MATILDE SALAMANCA SpA",
        rut: "770856462",
        type: "EMPRESA",
        bienes: [
            {
                source: "Conservador de Bienes Raíces",
                url: "https://conservadoresdigitales.cl/conservador/santiago/consultas-en-linea/indice-de-propiedad",
                headers: ["Foja", "Número", "Año", "Dirección"],
                values: [
                    ["44988", "65470", "2010", "Valenzuela Castillo 1666"],
                    ["45060", "65576", "2014", "Matilde Salamanca 841"],
                    ["44062", "64097", "2010", "Valenzuela Castillo 1292"],
                    ["50299", "73019", "2020", "Calle Matilde Salamanca 857"],
                    ["90181", "131087", "2014", "Matilde Salamanca 821"],
                    ["74957", "109084", "2020", "Federico Froebel 1676"],
                    ["74958", "109086", "2020", "Eliodoro Yanez 1687"]
                ]
            },
            {
                source: "CMF",
                url: "https://www.cmfchile.cl/portal/principal/613/w3-channel.html",
                headers: ["Razón Social", "RUT", "Acciones (%)"],
                values: [
                    ["INMOBILIARIA POCURO SUR SPA", "76.133.622-3", ">20%"]
                ]
            },
        ]
    },
    {
        name: "MARJORIE DANIELA MELLA FIGUEROA",
        rut: "152531842",
        type: "PERSONA",
        bienes: [
            {
                source: "deQuiénes",
                url: "https://dequienes.cl/",
                headers: ["Empresa", "RUT", "Socio"],
                values: [
                    ["SOCIEDAD COMERCIAL SAN LUIS LIMITADA", "76.648.704-1", "Sí"]
                ]
            },
            {
                source: "CMF",
                url: "https://www.cmfchile.cl/portal/principal/613/w3-channel.html",
                headers: ["Razón Social", "RUT", "Acciones (%)"],
                values: [
                    ["TELEFONICA MOVILES CHILE SA", "76.124.890-1", ">20%"]
                ]
            }
        ]
    },
    {
        name: "OBRAS DE INGENIERÍA PUYEVIAL SpA",
        rut: "766891225",
        type: "EMPRESA",
        bienes: [ ],
    },
];