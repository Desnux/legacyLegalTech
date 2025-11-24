import { SuggestionResponse } from "@/services/response";
import { Case, CaseStats, CaseStatsResponse } from "@/types/case";
import { Receptor, Tasks } from "@/types/recepthor";

export interface StatisticsData {
    start_amount: string;
    end_amount: string;
    quantity: number;
    amount: number;
}

export const statisticsData: StatisticsData[] = [
    {
        "start_amount": '0M',
        "end_amount": '50M',
        "quantity": 90,
        "amount": 800000000000
    },
    {
        "start_amount": '50M',
        "end_amount": '100M',
        "quantity": 41,
        "amount": 80000000000
    },
    {
        "start_amount": '100M',
        "end_amount": '150M',
        "quantity": 19,
        "amount": 8000000000
    },
    {
        "start_amount": '150M',
        "end_amount": '200M',
        "quantity": 34,
        "amount": 8000000000
    },
    {
        "start_amount": '200M',
        "end_amount": '',
        "quantity": 18,
        "amount": 16000000000
    }
];


export interface CaseTableData {
    event_type: string;
    time: string;
    period: number;
    quantity: number;
    quantity_in_period: number;
    quantity_out_period: number;
    amount: number;
    recovered_amount: number;
    pending_amount: number;
    quantity_detail: QuantityDetail[];
}

export interface QuantityDetail {
    lawyer_office: string;
    quantity: number;
    amount: number;
}

export const statisticsData2: CaseTableData[] = [
    {
        "event_type": "documents",
        "time": '17 Días aprox.',
        "period": 15,
        "quantity": 41,
        "quantity_in_period": 31,
        "quantity_out_period": 10,
        "amount": 50000000,
        "recovered_amount": 35000000,
        "pending_amount": 15000000,
        "quantity_detail": [
            {
                "lawyer_office": "IFBL Abogados",
                "quantity": 31,
                "amount": 50000000
            },
            {
                "lawyer_office": "Braun y Asociados",
                "quantity": 10,
                "amount": 50000000
            },
            
        ]
    },    
    {
        "event_type": "dispatch_start",
        "time": '24 Días aprox.',
        "period": 22,
        "quantity": 34,
        "quantity_in_period": 10,
        "quantity_out_period": 24,
        "amount": 150000000,
        "recovered_amount": 120000000,
        "pending_amount": 30000000,
        "quantity_detail": [
            {
                "lawyer_office": "IFBL Abogados",
                "quantity": 4,
                "amount": 150000000
            },
            {
                "lawyer_office": "Braun y Asociados",
                "quantity": 30,
                "amount": 100000000
            },
        ]
    },
    {
        "event_type": "notification",
        "time": '19 Días aprox.',
        "period": 15,
        "quantity": 8,
        "quantity_in_period": 4,
        "quantity_out_period": 4,
        "amount": 200000000,
        "recovered_amount": 160000000,
        "pending_amount": 40000000,
        "quantity_detail": [
            {
                "lawyer_office": "IFBL Abogados",
                "quantity": 4,
                "amount": 200000000
            },
            {
                "lawyer_office": "Braun y Asociados",
                "quantity": 4,
                "amount": 100000000
            },
        ]
    },
    {
        "event_type": "defense",
        "time": '16 Días aprox.',
        "period": 17,
        "quantity": 10,
        "quantity_in_period": 3,
        "quantity_out_period": 7,
        "amount": 250000000,
        "recovered_amount": 200000000,
        "pending_amount": 50000000,
        "quantity_detail": [
            {
                "lawyer_office": "IFBL Abogados",
                "quantity": 5,
                "amount": 250000000
            },
            {
                "lawyer_office": "Braun y Asociados",
                "quantity": 5,
                "amount": 100000000
            },
        ]
    },
    {   
        "event_type": "plaintiff_answer",
        "time": '12 Días aprox.',
        "period": 15,
        "quantity": 10,
        "quantity_in_period": 4,
        "quantity_out_period": 6,
        "amount": 300000000,
        "recovered_amount": 240000000,
        "pending_amount": 60000000,
        "quantity_detail": [
            {
                "lawyer_office": "IFBL Abogados",
                "quantity": 6,
                "amount": 300000000
            },
            {
                "lawyer_office": "Braun y Asociados",
                "quantity": 4,
                "amount": 100000000
            },
        ]
    },
    {
        "event_type": "finished",
        "time": '13 Días aprox.',
        "period": 12,
        "quantity": 10,
        "quantity_in_period": 7,
        "quantity_out_period": 3,
        "amount": 350000000,
        "recovered_amount": 280000000,
        "pending_amount": 70000000,
        "quantity_detail": [
            {
                "lawyer_office": "IFBL Abogados",
                "quantity": 1,
                "amount": 350000000
            },
            {
                "lawyer_office": "Braun y Asociados",
                "quantity": 9,
                "amount": 100000000
            },
        ]
    },
	{
        "event_type": "sentence",
        "time": '22 Días aprox.',
        "period": 20,
        "quantity": 19,
        "quantity_in_period": 10,
        "quantity_out_period": 9,
        "amount": 100000000,
        "recovered_amount": 75000000,
        "pending_amount": 25000000,
        "quantity_detail": [
            {
                "lawyer_office": "IFBL Abogados",
                "quantity": 10,
                "amount": 100000000
            },
            {
                "lawyer_office": "Braun y Asociados",
                "quantity": 9,
                "amount": 100000000
            },
        ]       
    }
];

export const statisticsData3 = [
    {
        "quantity": 102,
        "amount": 8000000000000
    }
];

export interface LawyerOfficeData {
    name: string;
    quantity: number;
    amount: number;
}

export const statisticsData4: LawyerOfficeData[] = [
    {
        "name": 'IFBL Abogados',
        "quantity": 25,
        "amount": 200000000
    },
    {
        "name": 'Braun y Asociados',
        "quantity": 30,
        "amount": 400000000
    }
];

// Datos de prueba para diferentes oficinas - IFBL Abogados
export const statisticsDataIFBL: StatisticsData[] = [
    {
        "start_amount": '0M',
        "end_amount": '50M',
        "quantity": 45,
        "amount": 400000000000
    },
    {
        "start_amount": '50M',
        "end_amount": '100M',
        "quantity": 20,
        "amount": 40000000000
    },
    {
        "start_amount": '100M',
        "end_amount": '150M',
        "quantity": 10,
        "amount": 4000000000
    },
    {
        "start_amount": '150M',
        "end_amount": '200M',
        "quantity": 15,
        "amount": 4000000000
    },
    {
        "start_amount": '200M',
        "end_amount": '',
        "quantity": 8,
        "amount": 8000000000
    }
];

// Datos de prueba para diferentes oficinas - Braun y Asociados
export const statisticsDataBraun: StatisticsData[] = [
    {
        "start_amount": '0M',
        "end_amount": '50M',
        "quantity": 45,
        "amount": 400000000000
    },
    {
        "start_amount": '50M',
        "end_amount": '100M',
        "quantity": 21,
        "amount": 40000000000
    },
    {
        "start_amount": '100M',
        "end_amount": '150M',
        "quantity": 9,
        "amount": 4000000000
    },
    {
        "start_amount": '150M',
        "end_amount": '200M',
        "quantity": 19,
        "amount": 4000000000
    },
    {
        "start_amount": '200M',
        "end_amount": '',
        "quantity": 10,
        "amount": 8000000000
    }
];

// Datos mock para milestones/trámites
export const mockMilestones = [
  {
    folio: "52",
    document: [],
    annex: [],
    stage: "Excepciones",
    procedure: "Resolución",
    procedureDescription: "Poder acreditado/acompaña patrocinio",
    procedureDate: "12/02/2021",
    page: "3",
    actionToFollow: "",
    responsiblePerson: "",
    deadline: ""
  },
  {
    folio: "51",
    document: [
      "https://www.pjud.cl/documents/resolucion_52.pdf",
      "https://www.pjud.cl/documents/anexo_52.pdf"
    ],
    annex: [
      "https://www.pjud.cl/annexes/evidencia_52.pdf",
      "https://www.pjud.cl/annexes/testimonio_52.pdf"
    ],
    stage: "Excepciones",
    procedure: "Resolución",
    procedureDescription: "Archivo del expediente en el Tribunal",
    procedureDate: "27/03/2025",
    page: "2",
    actionToFollow: "Presentar recursos de apelación",
    responsiblePerson: "Equipo Legal",
    deadline: "2025-04-10"
  },
  {
    folio: "50",
    document: [
      "https://www.pjud.cl/documents/notificacion_51.pdf"
    ],
    annex: [
      "https://www.pjud.cl/annexes/certificacion_51.pdf"
    ],
    stage: "Excepciones",
    procedure: "Actuación Receptor",
    procedureDescription: "Notificación por cédula de otras resoluciones (Certificación) Diligencia: 26/09/2024 14:40. Este trámite incluye la presentación de documentación adicional requerida por el tribunal, incluyendo certificaciones de notificación y evidencia de cumplimiento de plazos establecidos en el procedimiento legal correspondiente.",
    procedureDate: "26/09/2024 (26/09/2024)",
    page: "0",
    actionToFollow: "Preparar respuesta a notificación",
    responsiblePerson: "Asistente Legal",
    deadline: "2024-10-15"
  },
  {
    folio: "49",
    document: [
      "https://www.pjud.cl/documents/notificacion_51.pdf"
    ],
    annex: [
      "https://www.pjud.cl/annexes/certificacion_51.pdf"
    ],
    stage: "Excepciones",
    procedure: "Actuación Receptor",
    procedureDescription: "Notificación por cédula de otras resoluciones (Certificación) Diligencia: 26/09/2024 14:40. Este trámite incluye la presentación de documentación adicional requerida por el tribunal, incluyendo certificaciones de notificación y evidencia de cumplimiento de plazos establecidos en el procedimiento legal correspondiente.",
    procedureDate: "26/09/2024 (26/09/2024)",
    page: "0",
    actionToFollow: "Preparar respuesta a notificación",
    responsiblePerson: "Asistente Legal",
    deadline: "2024-10-15"
  },
  {
    folio: "48",
    document: [
      "https://www.pjud.cl/documents/notificacion_51.pdf"
    ],
    annex: [
      "https://www.pjud.cl/annexes/certificacion_51.pdf"
    ],
    stage: "Excepciones",
    procedure: "Actuación Receptor",
    procedureDescription: "Notificación por cédula de otras resoluciones (Certificación) Diligencia: 26/09/2024 14:40. Este trámite incluye la presentación de documentación adicional requerida por el tribunal, incluyendo certificaciones de notificación y evidencia de cumplimiento de plazos establecidos en el procedimiento legal correspondiente.",
    procedureDate: "26/09/2024 (26/09/2024)",
    page: "0",
    actionToFollow: "Preparar respuesta a notificación",
    responsiblePerson: "Asistente Legal",
    deadline: "2024-10-15"
  },
  {
    folio: "47",
    document: [
      "https://www.pjud.cl/documents/notificacion_51.pdf"
    ],
    annex: [
      "https://www.pjud.cl/annexes/certificacion_51.pdf"
    ],
    stage: "Excepciones",
    procedure: "Actuación Receptor",
    procedureDescription: "Notificación por cédula de otras resoluciones (Certificación) Diligencia: 26/09/2024 14:40. Este trámite incluye la presentación de documentación adicional requerida por el tribunal, incluyendo certificaciones de notificación y evidencia de cumplimiento de plazos establecidos en el procedimiento legal correspondiente.",
    procedureDate: "26/09/2024 (26/09/2024)",
    page: "0",
    actionToFollow: "Preparar respuesta a notificación",
    responsiblePerson: "Asistente Legal",
    deadline: "2024-10-15"
  },
  {
    folio: "46",
    document: [
      "https://www.pjud.cl/documents/notificacion_51.pdf"
    ],
    annex: [
      "https://www.pjud.cl/annexes/certificacion_51.pdf"
    ],
    stage: "Excepciones",
    procedure: "Actuación Receptor",
    procedureDescription: "Notificación por cédula de otras resoluciones (Certificación) Diligencia: 26/09/2024 14:40. Este trámite incluye la presentación de documentación adicional requerida por el tribunal, incluyendo certificaciones de notificación y evidencia de cumplimiento de plazos establecidos en el procedimiento legal correspondiente.",
    procedureDate: "26/09/2024 (26/09/2024)",
    page: "0",
    actionToFollow: "Preparar respuesta a notificación",
    responsiblePerson: "Asistente Legal",
    deadline: "2024-10-15"
  },
  {
    folio: "45",
    document: [
      "https://www.pjud.cl/documents/notificacion_51.pdf"
    ],
    annex: [
      "https://www.pjud.cl/annexes/certificacion_51.pdf"
    ],
    stage: "Excepciones",
    procedure: "Actuación Receptor",
    procedureDescription: "Notificación por cédula de otras resoluciones (Certificación) Diligencia: 26/09/2024 14:40. Este trámite incluye la presentación de documentación adicional requerida por el tribunal, incluyendo certificaciones de notificación y evidencia de cumplimiento de plazos establecidos en el procedimiento legal correspondiente.",
    procedureDate: "26/09/2024 (26/09/2024)",
    page: "0",
    actionToFollow: "Preparar respuesta a notificación",
    responsiblePerson: "Asistente Legal",
    deadline: "2024-10-15"
  },
  {
    folio: "44",
    document: [
      "https://www.pjud.cl/documents/notificacion_51.pdf"
    ],
    annex: [
      "https://www.pjud.cl/annexes/certificacion_51.pdf"
    ],
    stage: "Excepciones",
    procedure: "Actuación Receptor",
    procedureDescription: "Notificación por cédula de otras resoluciones (Certificación) Diligencia: 26/09/2024 14:40. Este trámite incluye la presentación de documentación adicional requerida por el tribunal, incluyendo certificaciones de notificación y evidencia de cumplimiento de plazos establecidos en el procedimiento legal correspondiente.",
    procedureDate: "26/09/2024 (26/09/2024)",
    page: "0",
    actionToFollow: "Preparar respuesta a notificación",
    responsiblePerson: "Asistente Legal",
    deadline: "2024-10-15"
  },
  {
    folio: "43",
    document: [
      "https://www.pjud.cl/documents/notificacion_51.pdf"
    ],
    annex: [
      "https://www.pjud.cl/annexes/certificacion_51.pdf"
    ],
    stage: "Excepciones",
    procedure: "Actuación Receptor",
    procedureDescription: "Notificación por cédula de otras resoluciones (Certificación) Diligencia: 26/09/2024 14:40. Este trámite incluye la presentación de documentación adicional requerida por el tribunal, incluyendo certificaciones de notificación y evidencia de cumplimiento de plazos establecidos en el procedimiento legal correspondiente.",
    procedureDate: "26/09/2024 (26/09/2024)",
    page: "0",
    actionToFollow: "Preparar respuesta a notificación",
    responsiblePerson: "Asistente Legal",
    deadline: "2024-10-15"
  },
  {
    folio: "42",
    document: [
      "https://www.pjud.cl/documents/notificacion_51.pdf"
    ],
    annex: [
      "https://www.pjud.cl/annexes/certificacion_51.pdf"
    ],
    stage: "Excepciones",
    procedure: "Actuación Receptor",
    procedureDescription: "Notificación por cédula de otras resoluciones (Certificación) Diligencia: 26/09/2024 14:40. Este trámite incluye la presentación de documentación adicional requerida por el tribunal, incluyendo certificaciones de notificación y evidencia de cumplimiento de plazos establecidos en el procedimiento legal correspondiente.",
    procedureDate: "26/09/2024 (26/09/2024)",
    page: "0",
    actionToFollow: "Preparar respuesta a notificación",
    responsiblePerson: "Asistente Legal",
    deadline: "2024-10-15"
  },
  {
    folio: "41",
    document: [
      "https://www.pjud.cl/documents/notificacion_51.pdf"
    ],
    annex: [
      "https://www.pjud.cl/annexes/certificacion_51.pdf"
    ],
    stage: "Excepciones",
    procedure: "Actuación Receptor",
    procedureDescription: "Notificación por cédula de otras resoluciones (Certificación) Diligencia: 26/09/2024 14:40. Este trámite incluye la presentación de documentación adicional requerida por el tribunal, incluyendo certificaciones de notificación y evidencia de cumplimiento de plazos establecidos en el procedimiento legal correspondiente.",
    procedureDate: "26/09/2024 (26/09/2024)",
    page: "0",
    actionToFollow: "Preparar respuesta a notificación",
    responsiblePerson: "Asistente Legal",
    deadline: "2024-10-15"
  }
];

// Datos para la tabla "Orden de Causas por Monto"
export interface CauseOrderData {
  id: number;
  cause: string;
  debtor: string;
  capital: number;
  interest: number;
  qualification?: string;
  terms?: string;
  analysis?: string;
  lawyer_office?: string;
  isSummary?: boolean;
  summaryType?: 'subtotal' | 'others' | 'total';
}

export const causeOrderData: CauseOrderData[] = [
  // Datos principales
  {
    id: 1,
    cause: "c14120-2025",
    debtor: "Constructora Inmobiliaria S.A.",
    capital: 1543000000,
    interest: 77150000,
    qualification: "Alto Riesgo",
    terms: "30 días",
    analysis: "",
    lawyer_office: "IFBL Abogados"
  },
  {
    id: 2,
    cause: "c24323-2025",
    debtor: "Comercializadora del Norte Ltda.",
    capital: 758000000,
    interest: 37900000,
    qualification: "Medio Riesgo",
    terms: "45 días",
    analysis: "",
    lawyer_office: "Braun y Asociados"
  },
  {
    id: 3,
    cause: "c00124-2025",
    debtor: "Transportes Rápidos Chile SPA",
    capital: 235600000,
    interest: 11780000,
    qualification: "Bajo Riesgo",
    terms: "15 días",
    analysis: "",
    lawyer_office: "IFBL Abogados"
  },
  {
    id: 4,
    cause: "c08901-2025",
    debtor: "Servicios Logísticos Integrales",
    capital: 189000000,
    interest: 9450000,
    qualification: "Medio Riesgo",
    terms: "60 días",
    analysis: "",
    lawyer_office: "Braun y Asociados"
  },
  {
    id: 5,
    cause: "c15602-2025",
    debtor: "Inversiones Financieras del Sur",
    capital: 456000000,
    interest: 22800000,
    qualification: "Alto Riesgo",
    terms: "90 días",
    analysis: "",
    lawyer_office: "IFBL Abogados"
  },
  {
    id: 6,
    cause: "c23403-2025",
    debtor: "Empresa de Telecomunicaciones Ltda.",
    capital: 321000000,
    interest: 16050000,
    qualification: "Bajo Riesgo",
    terms: "20 días",
    analysis: "",
    lawyer_office: "Braun y Asociados"
  },
  {
    id: 7,
    cause: "c06704-2025",
    debtor: "Comercial del Pacífico S.A.",
    capital: 278000000,
    interest: 13900000,
    qualification: "Medio Riesgo",
    terms: "40 días",
    analysis: "",
    lawyer_office: "IFBL Abogados"
  },
  {
    id: 8,
    cause: "c44505-2025",
    debtor: "Constructora Metropolitana",
    capital: 892000000,
    interest: 44600000,
    qualification: "Alto Riesgo",
    terms: "120 días",
    analysis: "",
    lawyer_office: "Braun y Asociados"
  },
  {
    id: 9,
    cause: "c12306-2025",
    debtor: "Servicios de Limpieza Profesional",
    capital: 145000000,
    interest: 7250000,
    qualification: "Bajo Riesgo",
    terms: "25 días",
    analysis: "",
    lawyer_office: "IFBL Abogados"
  },
  {
    id: 10,
    cause: "c33407-2025",
    debtor: "Distribuidora Nacional de Alimentos",
    capital: 102000000,
    interest: 5100000,
    qualification: "Medio Riesgo",
    terms: "35 días",
    analysis: "",
    lawyer_office: "Braun y Asociados"
  },
  {
    id: 11,
    cause: "c56708-2025",
    debtor: "Inmobiliaria Costanera Center",
    capital: 678000000,
    interest: 33900000,
    qualification: "Alto Riesgo",
    terms: "180 días",
    analysis: "",
    lawyer_office: "IFBL Abogados"
  },
  {
    id: 12,
    cause: "c78909-2025",
    debtor: "Empresa de Energía Renovable",
    capital: 445000000,
    interest: 22250000,
    qualification: "Medio Riesgo",
    terms: "50 días",
    analysis: "",
    lawyer_office: "Braun y Asociados"
  }
];

export const RECEPTORS_MOCK_DATA: Receptor[] = [
		{
			"address": "Huérfanos n° 1.373, oficina n°305",
			"id": "012ab7aa-eccf-48a4-97ac-8fcda27ee175",
			"name": "Gabriel Antonio Carreño Rivas",
			"primaryEmail": "receptorjudicial@gmail.com",
			"primaryPhone": "+56 9 4197 9360",
			"profiles": [
				{
					"tribunalId": "5abe6da5-07ab-4724-81a3-038f3f2d34cb",
					"tribunalName": "1º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "eaf8f716-2810-4e88-9bc4-1a6538e64f19",
					"tribunalName": "2º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "7f4aa170-b7c4-4946-b2fa-030ae126cbff",
					"tribunalName": "3º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "bd45f92a-6798-4370-a6fd-236683d91ddd",
					"tribunalName": "4º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "fbfa3c59-04d0-49cd-b3ee-7d41e71a694c",
					"tribunalName": "5º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "e8015f2f-b6ec-4126-a329-fbd3ec362a05",
					"tribunalName": "6º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "ec4f79d7-517f-423b-9afb-1e62d127bf3c",
					"tribunalName": "7º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "9eb907be-bc98-480f-b6c5-f8e7ae99f955",
					"tribunalName": "8º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "b4a19e94-e75e-4ae3-af18-28198772d3d9",
					"tribunalName": "9º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "dfa4889f-5bae-4155-9812-1a29bcaf2fb8",
					"tribunalName": "10º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "9af8e842-c137-4773-98b0-a762b126a875",
					"tribunalName": "11º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "3fb4ba94-6f20-4311-92f5-295ec36e7efe",
					"tribunalName": "12º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "1a561ecd-746c-44c0-a20d-3c879dca79cc",
					"tribunalName": "13º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "9f19874c-2aa6-4007-a1bc-d4717eb61c44",
					"tribunalName": "14º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "02bbd61e-8d73-4560-bb24-6121872a9a7e",
					"tribunalName": "15º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "473d4e1c-7a3d-414d-b669-e507cd627235",
					"tribunalName": "16º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "8eb54695-ca7e-4917-863c-5874ed7cfe1b",
					"tribunalName": "17º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "90be324f-d92f-44dc-ae47-ff6427166cf8",
					"tribunalName": "18º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "98524567-95bb-413b-b84a-7242c85cd0b2",
					"tribunalName": "19º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "cb72fe03-accc-4a59-b155-5d64cff256db",
					"tribunalName": "20º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "52127cfc-c157-4388-94c3-4f21976adb77",
					"tribunalName": "21º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "00d6afcf-a155-43f5-9b0e-05826671004c",
					"tribunalName": "22º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "df8748fb-50f6-4a07-9785-cce37afb3ef2",
					"tribunalName": "23º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "bc3cc5f0-21bb-4d04-bec2-0a429d6acd42",
					"tribunalName": "24º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "16bc0c8c-73b2-4d94-9ad0-68677b4f8e59",
					"tribunalName": "25º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "be0303dd-3b47-458a-98ea-a9743af1ab65",
					"tribunalName": "26º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "632bf4dc-494e-475a-a71f-ca1b4741e4f2",
					"tribunalName": "27º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "70d4ff78-86ae-45c7-a1e8-6c3405307b48",
					"tribunalName": "28º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "71bf0311-ddee-4490-8c2c-f03c47f159ea",
					"tribunalName": "29º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "ad0e10c8-779b-483a-aee2-8ef43ab0089b",
					"tribunalName": "30º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "6a56f4ed-075f-4f5e-8a45-8a0ae8bae252",
					"tribunalName": "Juzgado de Letras de Colina"
				}
			],
			"secondaryEmail": "",
			"secondaryPhone": "+56 2 2672 3784",
			"user": {
				"firstName": "Gabriel Antonio Carreño Rivas",
				"id": "9eba6537-f7e2-4167-968f-2ac195e84e4d",
				"lastName": ""
			}
		},
		{
			"address": "Compañía n°1.390, oficina n°2.103",
			"id": "025330dd-3eb2-47de-8a06-733cb5a2e1b8",
			"name": "Jorge Arturo Leiva Franco",
			"primaryEmail": "jorgeleiva.receptor@gmail.com",
			"primaryPhone": "+56 9 9158 5156",
			"profiles": [
				{
					"tribunalId": "5abe6da5-07ab-4724-81a3-038f3f2d34cb",
					"tribunalName": "1º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "eaf8f716-2810-4e88-9bc4-1a6538e64f19",
					"tribunalName": "2º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "7f4aa170-b7c4-4946-b2fa-030ae126cbff",
					"tribunalName": "3º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "bd45f92a-6798-4370-a6fd-236683d91ddd",
					"tribunalName": "4º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "fbfa3c59-04d0-49cd-b3ee-7d41e71a694c",
					"tribunalName": "5º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "e8015f2f-b6ec-4126-a329-fbd3ec362a05",
					"tribunalName": "6º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "ec4f79d7-517f-423b-9afb-1e62d127bf3c",
					"tribunalName": "7º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "9eb907be-bc98-480f-b6c5-f8e7ae99f955",
					"tribunalName": "8º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "b4a19e94-e75e-4ae3-af18-28198772d3d9",
					"tribunalName": "9º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "dfa4889f-5bae-4155-9812-1a29bcaf2fb8",
					"tribunalName": "10º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "9af8e842-c137-4773-98b0-a762b126a875",
					"tribunalName": "11º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "3fb4ba94-6f20-4311-92f5-295ec36e7efe",
					"tribunalName": "12º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "1a561ecd-746c-44c0-a20d-3c879dca79cc",
					"tribunalName": "13º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "9f19874c-2aa6-4007-a1bc-d4717eb61c44",
					"tribunalName": "14º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "02bbd61e-8d73-4560-bb24-6121872a9a7e",
					"tribunalName": "15º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "473d4e1c-7a3d-414d-b669-e507cd627235",
					"tribunalName": "16º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "8eb54695-ca7e-4917-863c-5874ed7cfe1b",
					"tribunalName": "17º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "90be324f-d92f-44dc-ae47-ff6427166cf8",
					"tribunalName": "18º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "98524567-95bb-413b-b84a-7242c85cd0b2",
					"tribunalName": "19º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "cb72fe03-accc-4a59-b155-5d64cff256db",
					"tribunalName": "20º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "52127cfc-c157-4388-94c3-4f21976adb77",
					"tribunalName": "21º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "00d6afcf-a155-43f5-9b0e-05826671004c",
					"tribunalName": "22º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "df8748fb-50f6-4a07-9785-cce37afb3ef2",
					"tribunalName": "23º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "bc3cc5f0-21bb-4d04-bec2-0a429d6acd42",
					"tribunalName": "24º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "16bc0c8c-73b2-4d94-9ad0-68677b4f8e59",
					"tribunalName": "25º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "be0303dd-3b47-458a-98ea-a9743af1ab65",
					"tribunalName": "26º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "632bf4dc-494e-475a-a71f-ca1b4741e4f2",
					"tribunalName": "27º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "70d4ff78-86ae-45c7-a1e8-6c3405307b48",
					"tribunalName": "28º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "71bf0311-ddee-4490-8c2c-f03c47f159ea",
					"tribunalName": "29º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "ad0e10c8-779b-483a-aee2-8ef43ab0089b",
					"tribunalName": "30º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "6a56f4ed-075f-4f5e-8a45-8a0ae8bae252",
					"tribunalName": "Juzgado de Letras de Colina"
				}
			],
			"secondaryEmail": "",
			"secondaryPhone": "+56 2 2698 6507",
			"user": {
				"firstName": "Jorge Arturo Leiva Franco",
				"id": "8c608492-c224-4c93-8caf-ed1eac929004",
				"lastName": ""
			}
		},
		{
			"address": "Rosa rodriguez n° 1375, oficina n°406",
			"id": "02f4658f-3132-4899-b060-8c9a4db3dec8",
			"name": "María Cecilia Schuler Gahona",
			"primaryEmail": "receptoraschuler@gmail.com",
			"primaryPhone": "+56 9 8428 2022",
			"profiles": [
				{
					"tribunalId": "5abe6da5-07ab-4724-81a3-038f3f2d34cb",
					"tribunalName": "1º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "eaf8f716-2810-4e88-9bc4-1a6538e64f19",
					"tribunalName": "2º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "7f4aa170-b7c4-4946-b2fa-030ae126cbff",
					"tribunalName": "3º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "bd45f92a-6798-4370-a6fd-236683d91ddd",
					"tribunalName": "4º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "fbfa3c59-04d0-49cd-b3ee-7d41e71a694c",
					"tribunalName": "5º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "e8015f2f-b6ec-4126-a329-fbd3ec362a05",
					"tribunalName": "6º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "ec4f79d7-517f-423b-9afb-1e62d127bf3c",
					"tribunalName": "7º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "9eb907be-bc98-480f-b6c5-f8e7ae99f955",
					"tribunalName": "8º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "b4a19e94-e75e-4ae3-af18-28198772d3d9",
					"tribunalName": "9º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "dfa4889f-5bae-4155-9812-1a29bcaf2fb8",
					"tribunalName": "10º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "9af8e842-c137-4773-98b0-a762b126a875",
					"tribunalName": "11º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "3fb4ba94-6f20-4311-92f5-295ec36e7efe",
					"tribunalName": "12º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "1a561ecd-746c-44c0-a20d-3c879dca79cc",
					"tribunalName": "13º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "9f19874c-2aa6-4007-a1bc-d4717eb61c44",
					"tribunalName": "14º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "02bbd61e-8d73-4560-bb24-6121872a9a7e",
					"tribunalName": "15º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "473d4e1c-7a3d-414d-b669-e507cd627235",
					"tribunalName": "16º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "8eb54695-ca7e-4917-863c-5874ed7cfe1b",
					"tribunalName": "17º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "90be324f-d92f-44dc-ae47-ff6427166cf8",
					"tribunalName": "18º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "98524567-95bb-413b-b84a-7242c85cd0b2",
					"tribunalName": "19º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "cb72fe03-accc-4a59-b155-5d64cff256db",
					"tribunalName": "20º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "52127cfc-c157-4388-94c3-4f21976adb77",
					"tribunalName": "21º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "00d6afcf-a155-43f5-9b0e-05826671004c",
					"tribunalName": "22º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "df8748fb-50f6-4a07-9785-cce37afb3ef2",
					"tribunalName": "23º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "bc3cc5f0-21bb-4d04-bec2-0a429d6acd42",
					"tribunalName": "24º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "16bc0c8c-73b2-4d94-9ad0-68677b4f8e59",
					"tribunalName": "25º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "be0303dd-3b47-458a-98ea-a9743af1ab65",
					"tribunalName": "26º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "632bf4dc-494e-475a-a71f-ca1b4741e4f2",
					"tribunalName": "27º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "70d4ff78-86ae-45c7-a1e8-6c3405307b48",
					"tribunalName": "28º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "71bf0311-ddee-4490-8c2c-f03c47f159ea",
					"tribunalName": "29º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "ad0e10c8-779b-483a-aee2-8ef43ab0089b",
					"tribunalName": "30º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "6a56f4ed-075f-4f5e-8a45-8a0ae8bae252",
					"tribunalName": "Juzgado de Letras de Colina"
				}
			],
			"secondaryEmail": "",
			"secondaryPhone": "+56 2 2699 0248",
			"user": {
				"firstName": "María Cecilia Schuler Gahona",
				"id": "f6444847-9f78-48b8-8e61-543cb506cfdf",
				"lastName": ""
			}
		},
		{
			"address": "Huerfanos n°1294, oficina n°43",
			"id": "035ad805-288a-4190-867f-da2d06942f14",
			"name": "Carlos Eduardo Pereira Penna",
			"primaryEmail": "receptor.cp@gmail.com",
			"primaryPhone": "+56 9 7574 3262",
			"profiles": [
				{
					"tribunalId": "5abe6da5-07ab-4724-81a3-038f3f2d34cb",
					"tribunalName": "1º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "eaf8f716-2810-4e88-9bc4-1a6538e64f19",
					"tribunalName": "2º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "7f4aa170-b7c4-4946-b2fa-030ae126cbff",
					"tribunalName": "3º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "bd45f92a-6798-4370-a6fd-236683d91ddd",
					"tribunalName": "4º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "fbfa3c59-04d0-49cd-b3ee-7d41e71a694c",
					"tribunalName": "5º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "e8015f2f-b6ec-4126-a329-fbd3ec362a05",
					"tribunalName": "6º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "ec4f79d7-517f-423b-9afb-1e62d127bf3c",
					"tribunalName": "7º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "9eb907be-bc98-480f-b6c5-f8e7ae99f955",
					"tribunalName": "8º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "b4a19e94-e75e-4ae3-af18-28198772d3d9",
					"tribunalName": "9º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "dfa4889f-5bae-4155-9812-1a29bcaf2fb8",
					"tribunalName": "10º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "9af8e842-c137-4773-98b0-a762b126a875",
					"tribunalName": "11º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "3fb4ba94-6f20-4311-92f5-295ec36e7efe",
					"tribunalName": "12º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "1a561ecd-746c-44c0-a20d-3c879dca79cc",
					"tribunalName": "13º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "9f19874c-2aa6-4007-a1bc-d4717eb61c44",
					"tribunalName": "14º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "02bbd61e-8d73-4560-bb24-6121872a9a7e",
					"tribunalName": "15º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "473d4e1c-7a3d-414d-b669-e507cd627235",
					"tribunalName": "16º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "8eb54695-ca7e-4917-863c-5874ed7cfe1b",
					"tribunalName": "17º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "90be324f-d92f-44dc-ae47-ff6427166cf8",
					"tribunalName": "18º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "98524567-95bb-413b-b84a-7242c85cd0b2",
					"tribunalName": "19º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "cb72fe03-accc-4a59-b155-5d64cff256db",
					"tribunalName": "20º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "52127cfc-c157-4388-94c3-4f21976adb77",
					"tribunalName": "21º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "00d6afcf-a155-43f5-9b0e-05826671004c",
					"tribunalName": "22º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "df8748fb-50f6-4a07-9785-cce37afb3ef2",
					"tribunalName": "23º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "bc3cc5f0-21bb-4d04-bec2-0a429d6acd42",
					"tribunalName": "24º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "16bc0c8c-73b2-4d94-9ad0-68677b4f8e59",
					"tribunalName": "25º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "be0303dd-3b47-458a-98ea-a9743af1ab65",
					"tribunalName": "26º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "632bf4dc-494e-475a-a71f-ca1b4741e4f2",
					"tribunalName": "27º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "70d4ff78-86ae-45c7-a1e8-6c3405307b48",
					"tribunalName": "28º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "71bf0311-ddee-4490-8c2c-f03c47f159ea",
					"tribunalName": "29º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "ad0e10c8-779b-483a-aee2-8ef43ab0089b",
					"tribunalName": "30º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "6a56f4ed-075f-4f5e-8a45-8a0ae8bae252",
					"tribunalName": "Juzgado de Letras de Colina"
				}
			],
			"secondaryEmail": "cepereirapenna@gmail.com",
			"secondaryPhone": "+56 2 2672 2866",
			"user": {
				"firstName": "Carlos Eduardo Pereira Penna",
				"id": "f8c0ea9b-e10d-44b2-a3b0-b305cffff456",
				"lastName": ""
			}
		},
		{
			"address": "Huerfanos n°1117, oficina n°427",
			"id": "039db65d-1814-4f3f-9118-d34d058d93bd",
			"name": "Marta Carolina Barrales Urbina",
			"primaryEmail": "carolinabarralesu@gmail.com",
			"primaryPhone": "+56 9 6209 4864",
			"profiles": [
				{
					"tribunalId": "5abe6da5-07ab-4724-81a3-038f3f2d34cb",
					"tribunalName": "1º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "eaf8f716-2810-4e88-9bc4-1a6538e64f19",
					"tribunalName": "2º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "7f4aa170-b7c4-4946-b2fa-030ae126cbff",
					"tribunalName": "3º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "bd45f92a-6798-4370-a6fd-236683d91ddd",
					"tribunalName": "4º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "fbfa3c59-04d0-49cd-b3ee-7d41e71a694c",
					"tribunalName": "5º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "e8015f2f-b6ec-4126-a329-fbd3ec362a05",
					"tribunalName": "6º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "ec4f79d7-517f-423b-9afb-1e62d127bf3c",
					"tribunalName": "7º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "9eb907be-bc98-480f-b6c5-f8e7ae99f955",
					"tribunalName": "8º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "b4a19e94-e75e-4ae3-af18-28198772d3d9",
					"tribunalName": "9º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "dfa4889f-5bae-4155-9812-1a29bcaf2fb8",
					"tribunalName": "10º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "9af8e842-c137-4773-98b0-a762b126a875",
					"tribunalName": "11º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "3fb4ba94-6f20-4311-92f5-295ec36e7efe",
					"tribunalName": "12º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "1a561ecd-746c-44c0-a20d-3c879dca79cc",
					"tribunalName": "13º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "9f19874c-2aa6-4007-a1bc-d4717eb61c44",
					"tribunalName": "14º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "02bbd61e-8d73-4560-bb24-6121872a9a7e",
					"tribunalName": "15º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "473d4e1c-7a3d-414d-b669-e507cd627235",
					"tribunalName": "16º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "8eb54695-ca7e-4917-863c-5874ed7cfe1b",
					"tribunalName": "17º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "90be324f-d92f-44dc-ae47-ff6427166cf8",
					"tribunalName": "18º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "98524567-95bb-413b-b84a-7242c85cd0b2",
					"tribunalName": "19º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "cb72fe03-accc-4a59-b155-5d64cff256db",
					"tribunalName": "20º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "52127cfc-c157-4388-94c3-4f21976adb77",
					"tribunalName": "21º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "00d6afcf-a155-43f5-9b0e-05826671004c",
					"tribunalName": "22º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "df8748fb-50f6-4a07-9785-cce37afb3ef2",
					"tribunalName": "23º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "bc3cc5f0-21bb-4d04-bec2-0a429d6acd42",
					"tribunalName": "24º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "16bc0c8c-73b2-4d94-9ad0-68677b4f8e59",
					"tribunalName": "25º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "be0303dd-3b47-458a-98ea-a9743af1ab65",
					"tribunalName": "26º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "632bf4dc-494e-475a-a71f-ca1b4741e4f2",
					"tribunalName": "27º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "70d4ff78-86ae-45c7-a1e8-6c3405307b48",
					"tribunalName": "28º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "71bf0311-ddee-4490-8c2c-f03c47f159ea",
					"tribunalName": "29º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "ad0e10c8-779b-483a-aee2-8ef43ab0089b",
					"tribunalName": "30º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "6a56f4ed-075f-4f5e-8a45-8a0ae8bae252",
					"tribunalName": "Juzgado de Letras de Colina"
				}
			],
			"secondaryEmail": "",
			"secondaryPhone": "",
			"user": {
				"firstName": "Marta Carolina Barrales Urbina",
				"id": "1d79b88c-e4eb-4434-8d28-c0de50daecc1",
				"lastName": ""
			}
		},
		{
			"address": "Compañía n° 1.390, oficina n°302",
			"id": "0553eb40-d7da-47a9-98b2-9ee0c888b49e",
			"name": "Germán Alejandro Camino Alzérreca",
			"primaryEmail": "germancaminoa@gmail.com",
			"primaryPhone": "+56 9 9229 0208",
			"profiles": [
				{
					"tribunalId": "5abe6da5-07ab-4724-81a3-038f3f2d34cb",
					"tribunalName": "1º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "eaf8f716-2810-4e88-9bc4-1a6538e64f19",
					"tribunalName": "2º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "7f4aa170-b7c4-4946-b2fa-030ae126cbff",
					"tribunalName": "3º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "bd45f92a-6798-4370-a6fd-236683d91ddd",
					"tribunalName": "4º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "fbfa3c59-04d0-49cd-b3ee-7d41e71a694c",
					"tribunalName": "5º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "e8015f2f-b6ec-4126-a329-fbd3ec362a05",
					"tribunalName": "6º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "ec4f79d7-517f-423b-9afb-1e62d127bf3c",
					"tribunalName": "7º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "9eb907be-bc98-480f-b6c5-f8e7ae99f955",
					"tribunalName": "8º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "b4a19e94-e75e-4ae3-af18-28198772d3d9",
					"tribunalName": "9º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "dfa4889f-5bae-4155-9812-1a29bcaf2fb8",
					"tribunalName": "10º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "9af8e842-c137-4773-98b0-a762b126a875",
					"tribunalName": "11º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "3fb4ba94-6f20-4311-92f5-295ec36e7efe",
					"tribunalName": "12º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "1a561ecd-746c-44c0-a20d-3c879dca79cc",
					"tribunalName": "13º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "9f19874c-2aa6-4007-a1bc-d4717eb61c44",
					"tribunalName": "14º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "02bbd61e-8d73-4560-bb24-6121872a9a7e",
					"tribunalName": "15º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "473d4e1c-7a3d-414d-b669-e507cd627235",
					"tribunalName": "16º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "8eb54695-ca7e-4917-863c-5874ed7cfe1b",
					"tribunalName": "17º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "90be324f-d92f-44dc-ae47-ff6427166cf8",
					"tribunalName": "18º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "98524567-95bb-413b-b84a-7242c85cd0b2",
					"tribunalName": "19º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "cb72fe03-accc-4a59-b155-5d64cff256db",
					"tribunalName": "20º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "52127cfc-c157-4388-94c3-4f21976adb77",
					"tribunalName": "21º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "00d6afcf-a155-43f5-9b0e-05826671004c",
					"tribunalName": "22º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "df8748fb-50f6-4a07-9785-cce37afb3ef2",
					"tribunalName": "23º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "bc3cc5f0-21bb-4d04-bec2-0a429d6acd42",
					"tribunalName": "24º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "16bc0c8c-73b2-4d94-9ad0-68677b4f8e59",
					"tribunalName": "25º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "be0303dd-3b47-458a-98ea-a9743af1ab65",
					"tribunalName": "26º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "632bf4dc-494e-475a-a71f-ca1b4741e4f2",
					"tribunalName": "27º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "70d4ff78-86ae-45c7-a1e8-6c3405307b48",
					"tribunalName": "28º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "71bf0311-ddee-4490-8c2c-f03c47f159ea",
					"tribunalName": "29º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "ad0e10c8-779b-483a-aee2-8ef43ab0089b",
					"tribunalName": "30º Juzgado Civil de Santiago"
				},
				{
					"tribunalId": "6a56f4ed-075f-4f5e-8a45-8a0ae8bae252",
					"tribunalName": "Juzgado de Letras de Colina"
				}
			],
			"secondaryEmail": "",
			"secondaryPhone": "+56 2 2697 4332",
			"user": {
				"firstName": "Germán Alejandro Camino Alzérreca",
				"id": "83db327d-70f0-4bbf-aae1-2af0e9a5fbb0",
				"lastName": ""
			}
		}
	];

export const TASKS_MOCK_DATA: Tasks[] = [
	{
		"address": "Huérfanos n° 1.373, oficina n°305",
		"addressDetails": "",
		"commune": "Santiago",
		"createdAt": "2025-10-03",
		"deadline": "2025-10-08",
		"firmCase": {
			"addedByUser": {
				"firstName": "Carlos Eduardo Pereira Penna",
				"id": "f8c0ea9b-e10d-44b2-a3b0-b305cffff456",
				"lastName": ""
			},
			"case": {
				"bookType": "1",
				"competence": "1",
				"id": "16a9f961-19ed-42ce-ade1-33254200fd1e",
				"rol": "1",
				"title": "1",
				"tribunal": {
					"court": {
						"id": "1",
						"name": "1",
					},
					"id": "1",
					"name": "1",
				},
				"year": "1"
			},
			"firm": {
				"id": "1",
				"name": "1",
			},
			"id": "1"
		},
		"id": "1",
		"notes": "",
		"quotes": [
			{
				"createdAt": new Date(),
				"dateOffered": new Date("2025-10-07"),
				"id": "1",
				"price": 100000,
				"receptor": {
					"id": "1",
					"primaryEmail": "receptorjudicial@gmail.com",
					"user": {
						"firstName": "Gabriel Antonio Carreño Rivas",
						"id": "1",
						"lastName": ""
					}
				},
				"status": "Pendiente",
				"updatedAt": new Date()
			},
			{
				"createdAt": new Date(),
				"dateOffered": new Date("2025-10-05"),
				"id": "2",
				"price": 200000,
				"receptor": {
					"id": "1",
					"primaryEmail": "jorgeleiva.receptor@gmail.com",
					"user": {
						"firstName": "Jorge Arturo Leiva Franco",
						"id": "1",
						"lastName": ""
					}
				},
				"status": "Pendiente",
				"updatedAt": new Date()
			},
			{
				"createdAt": new Date(),
				"dateOffered": new Date("2025-10-07"),
				"id": "3",
				"price": 300000,
				"receptor": {
					"id": "1",
					"primaryEmail": "receptoraschuler@gmail.com",
					"user": {
						"firstName": "María Cecilia Schuler Gahona",
						"id": "1",
						"lastName": ""
					}
				},
				"status": "Pendiente",
				"updatedAt": new Date()
			},
		],
		"region": "Santiago",
		"status": "pending",
		"summary": null,
		"updatedAt": new Date()
	}
];
	

export const RESPONSE_TEXT_MOCK_DATA: SuggestionResponse = {
		"message": "Valid",
		"code": 200,
		"suggestions": [
			{
				"id": "4aff9ad4-0208-4447-8723-2d0b3aae9bc6",
				"name": "Respuesta a la excepción de prescripción de deuda",
				"content": {
					"summary": "EN LO PRINCIPAL: EVACUA TRASLADO; PRIMER OTROSÍ: SE SOLICITA DEMOSTRAR INTERRUPCIONES VÁLIDAS DEL PLAZO",
					"court": "S.J.L. CIVIL DE SANTIAGO (4º)",
					"opening": "Raimundo Echeverría, abogado, por el ejecutante, Banco Consorcio, en los autos caratulados “Santander Consumer Finance Limitada/Biadayoli”, ROL C-2524-2022, a US., con respeto digo:\n\nQue por este acto, y estando dentro de plazo, vengo en evacuar traslado conferido con fecha 13 de octubre de 2025, respecto de las excepciones que fueron opuestas por los demandados, Elisa Natalia Antezana Barrios y Scotiabank Sud Americano, solicitando que éstas sean rechazadas en todas sus partes, en atención a los argumentos de hecho y fundamentos de derecho que se exponen a continuación:",
					"exception_responses": [
						"1) Respecto de la excepción de Nº 17 del artículo 464 del Código de Procedimiento Civil, esto es, la prescripción de la deuda o sólo de la acción ejecutiva: \n\nLa parte demandada sostiene que la acción ejecutiva está prescrita, basándose en que ha transcurrido más de un año desde el incumplimiento del deudor el 5 de octubre de 2021, lo que activó la aceleración del crédito y el vencimiento del pagaré, hasta la fecha de esta escritura. Según el artículo 98 de la Ley N° 18.092, el plazo de prescripción para los pagarés es de un año.\n\nSin embargo, la parte demandante rebate esta excepción señalando que, aunque el plazo de prescripción para los pagarés es de un año, existen circunstancias que interrumpen o suspenden dicho plazo. En este caso, la presentación de la demanda ejecutiva y las acciones judiciales emprendidas por el acreedor constituyen actos que interrumpen la prescripción, conforme a lo dispuesto en el artículo 2518 del Código Civil, que establece que la prescripción se interrumpe civilmente por la demanda judicial. Además, el pagaré N°710122497372, suscrito el 18 de octubre de 2021, aún se encuentra dentro del plazo de prescripción, ya que la demanda fue presentada antes de que transcurriera un año desde el vencimiento de la obligación.\n\nPor lo tanto, no se configuran los presupuestos para alegar la prescripción de la acción ejecutiva, y la excepción debe ser rechazada en todas sus partes."
					],
					"main_request": "POR TANTO,\n\nRUEGO A US. tener por evacuado el traslado conferido y, en su mérito, se rechace cada una de las excepciones hechas valer por el demandado, con expresa condena en costas.\n\nEn virtud de lo anterior, se solicita que se proceda conforme a derecho, asegurando el cumplimiento de las obligaciones legales pertinentes y garantizando la equidad en el proceso judicial en curso. Se enfatiza la importancia de mantener la integridad del procedimiento legal, respetando los principios de justicia y equidad que rigen nuestro ordenamiento jurídico.\n\nSe espera que la resolución de este asunto se lleve a cabo con la debida diligencia y en estricto apego a las normativas vigentes, a fin de salvaguardar los derechos e intereses legítimos de las partes involucradas. La presente solicitud se formula con el propósito de asegurar un desenlace justo y equitativo, en consonancia con los preceptos legales aplicables.\n\nSin otro particular, se reitera la solicitud de desestimar las excepciones planteadas, con la correspondiente imposición de costas al demandado, en atención a los fundamentos expuestos y en aras de la justicia y el derecho.",
					"additional_requests": "PRIMER OTROSÍ: RUEGO A US. tener presente que, en virtud de lo dispuesto en el artículo correspondiente del Código Civil, la excepción de prescripción invocada por la parte demandada no resulta aplicable al presente caso, dado que el plazo de prescripción no ha transcurrido en su totalidad. Asimismo, se debe considerar que han existido interrupciones válidas del plazo de prescripción, conforme a lo establecido en la normativa vigente, las cuales han sido debidamente documentadas y presentadas ante este Honorable Tribunal.\n\nEn consecuencia, solicito respetuosamente que se desestime la excepción de prescripción planteada, permitiendo así la continuación del proceso judicial en curso, en aras de garantizar el derecho a la tutela judicial efectiva y el acceso a la justicia de la parte demandante. Se adjuntan a la presente los documentos que acreditan las interrupciones mencionadas, para su debida consideración y análisis por parte de este Ilustre Juzgado.\n\nPor lo expuesto, solicito se sirva a tener en cuenta lo aquí manifestado al momento de resolver sobre la excepción de prescripción, en aras de asegurar una resolución justa y conforme a derecho. Es justicia que se pide en [lugar], a [fecha]."
				},
				"score": 0.9,
				"type": "exceptions_response"
			},
			{
				"id": "ede6b9d2-aa96-4072-ad64-3a36dd27a687",
				"name": "Argumento sobre la interrupción de la prescripción",
				"content": {
					"summary": "EN LO PRINCIPAL: EVACUA TRASLADO; PRIMER OTROSÍ: MEDIOS DE PRUEBA",
					"court": "S.J.L. CIVIL DE SANTIAGO (4º)",
					"opening": "Raimundo Echeverría, abogado, por el ejecutante, Banco Consorcio, en los autos caratulados “Santander Consumer Finance Limitada/Biadayoli”, ROL C-2524-2022, a US., con respeto digo:\n\nQue por este acto, y estando dentro de plazo, vengo en evacuar traslado conferido con fecha 13 de octubre de 2025, respecto de las excepciones que fueron opuestas por los demandados, Elisa Natalia Antezana Barrios y Scotiabank Sud Americano, solicitando que éstas sean rechazadas en todas sus partes, en atención a los argumentos de hecho y fundamentos de derecho que se exponen a continuación:",
					"exception_responses": [
						"1) Respecto de la excepción de Nº 17 del artículo 464 del Código de Procedimiento Civil, esto es, la prescripción de la deuda o sólo de la acción ejecutiva: \n\nLa parte demandada alega que la acción ejecutiva está prescrita, basándose en que ha transcurrido más de un año desde el incumplimiento del deudor el 5 de octubre de 2021, lo que activó la aceleración del crédito y el vencimiento del pagaré, hasta la fecha de esta escritura. Según el artículo 98 de la Ley N° 18.092, el plazo de prescripción para los pagarés es de un año.\n\nSin embargo, la parte demandante rebate esta excepción señalando que, conforme a los antecedentes presentados, la demanda ejecutiva fue interpuesta dentro del plazo legal, ya que el plazo de prescripción fue interrumpido por acciones legales previas, como la presentación de la demanda ejecutiva, que se realizó antes de que transcurriera el año desde el vencimiento de la obligación. Además, no existe evidencia de que el deudor haya realizado un reconocimiento de deuda que interrumpa el plazo de prescripción, pero la acción legal iniciada es suficiente para considerar que el plazo no ha transcurrido en su totalidad.\n\nPor lo tanto, no se configuran los presupuestos para alegar la prescripción de la acción ejecutiva, y la excepción debe ser rechazada en todas sus partes."
					],
					"main_request": "POR TANTO,\n\nRUEGO A US. tener por evacuado el traslado conferido y, en su mérito, se rechace cada una de las excepciones hechas valer por el demandado, con expresa condena en costas.",
					"additional_requests": "PRIMER OTROSÍ: SE RUEGA A US. tener presente que, en representación de mi parte, se hará uso de los siguientes medios de prueba, conforme a lo establecido en la normativa vigente: documentos instrumentales, declaraciones de testigos, confesiones de las partes, inspección personal del Tribunal, informes periciales, y presunciones legales. Asimismo, se presentará evidencia que demuestre que el plazo de prescripción ha sido interrumpido, ya sea por acciones legales previas o por el reconocimiento expreso de la deuda por parte del deudor, conforme a lo dispuesto en el Código Civil y demás legislación aplicable. Se solicita que estas pruebas sean debidamente valoradas en el contexto del presente procedimiento judicial, a fin de garantizar el respeto a los principios de justicia y equidad que rigen nuestro ordenamiento jurídico."
				},
				"score": 0.8,
				"type": "exceptions_response"
			},
			{
				"id": "29a3a036-ee1f-453b-acd5-01dcaf4854e2",
				"name": "Avenimiento",
				"content": {
					"header": "JUZGADO : 4º CIVIL DE SANTIAGO\nCAUSA ROL : C-2524-2022\nCARATULADO : SANTANDER CONSUMER FINANCE LIMITADA/BIADAYOLI\nCUADERNO : PRINCIPAL",
					"summary": "EN LO PRINCIPAL: AVENIMIENTO",
					"court": "S.J.L.",
					"opening": "Raimundo Echeverría, abogado, por el ejecutante, Banco Consorcio, en estos autos ejecutivos caratulados “Banco Consorcio/Antezana Barrios” , Rol C-2524-2022 , a US. respetuosamente digo:\n\nQue, con objeto de poner término al presente procedimiento, venimos a presentar los siguientes términos de avenimiento, para aprobación de este Tribunal:",
					"compromise_terms": "I: La demandada, doña Elisa Natalia Antezana Barrios, pagará la suma total de $41.689.870.- (cuarenta y un millones seiscientos ochenta y nueve mil ochocientos setenta pesos), por concepto de deuda capital, intereses y recargos por mora, en los siguientes términos:\n\n- Un abono inicial por la suma de $10.000.000.- (diez millones de pesos).\n\n- El saldo restante se pagará en 10 cuotas mensuales, iguales y sucesivas de $3.168.987.- (tres millones ciento sesenta y ocho mil novecientos ochenta y siete pesos), más los intereses correspondientes, pagaderas los días 13 de cada mes, a contar de noviembre de 2025.\n\n- Cada una de las cuotas se pagará en su equivalente en pesos, a la fecha de pago efectivo.\n\nII: Todos los pagos se efectuarán mediante depósito o transferencia electrónica, en la cuenta cuyo titular es Banco Consorcio, RUT N° 99.500.410-0, enviando copia a las casillas de correo del abogado patrocinante Raimundo Echeverría.\n\nIII: Las partes estipulan que, solo una vez cumplido este avenimiento, y el pago del total de las cuotas estipuladas, se dará término al juicio.\n\nIV: Del mismo modo, las partes estipulan que no verificado el pago en la fecha y condiciones estipuladas, Banco Consorcio podrá demandar el cumplimiento del avenimiento en el presente juicio o iniciar una ejecución nueva.\n\nV: Como consecuencia de los acuerdos antes indicados, las partes litigantes renuncian al ejercicio de las defensas empleadas, y de las que en derecho pueden hacer valer en esta causa, otorgándose el más completo y total finiquito, salvo el que emane del incumplimiento del presente avenimiento",
					"main_request": "POR TANTO,\n\nROGAMOS A US. aprobar los términos del presente avenimiento sometido a su aprobación.",
					"additional_requests": null
				},
				"score": 0.1,
				"type": "compromise"
			},
			{
				"id": "4ca223d3-014f-4bc0-ba7d-c3ba288ad60d",
				"name": "Desistimiento",
				"content": {
					"header": "JUZGADO : 4º CIVIL DE SANTIAGO\nCAUSA ROL : C-2524-2022\nCARATULADO : SANTANDER CONSUMER FINANCE LIMITADA/BIADAYOLI\nCUADERNO : PRINCIPAL",
					"summary": "EN LO PRINCIPAL: SE DESISTE DE DEMANDA EN LOS TÉRMINOS QUE INDICA",
					"court": "S.J.L.",
					"content": "Raimundo Echeverría, abogado, por el ejecutante, en estos autos ejecutivos caratulados “Santander Consumer Finance Limitada/Biadayoli”, Rol C-2524-2022, a US. respetuosamente decimos:\n\nEn uso del derecho que nos confiere el artículo 467 del Código de Procedimiento Civil, vengo en desistirme de la demanda ejecutiva interpuesta en contra de doña Elisa Natalia Antezana Barrios, en su calidad de deudora principal, y en contra de Scotiabank Sud Americano, en su calidad de aval, fiador y codeudor solidario.",
					"main_request": "POR TANTO,\n\nRUEGO A US., en mérito de lo dispuesto en el artículo 467 del Código de Procedimiento Civil, se sirva tener a esta parte por desistida de la demanda ejecutiva en contra de doña Elisa Natalia Antezana Barrios, en su calidad de deudora principal, y en contra de Scotiabank Sud Americano, en su calidad de aval, fiador y codeudor solidario."
				},
				"score": 0.05,
				"type": "withdrawal"
			}
		],
		"event_id": "0d661ad9-f65b-4c06-8866-555563ea2749"
	}