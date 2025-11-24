import { RJSFSchema } from "@rjsf/utils";

const RUT_PATTERN = "^(\\d{1,2}\\.\\d{3}\\.\\d{3}-[\\dkK])$";

const today = new Date().toISOString().split("T")[0];
const now = new Date();
const defaultDateTime = [
  now.getFullYear(),
  pad(now.getMonth() + 1),
  pad(now.getDate()),
].join("-")
  + "T"
  + [ pad(now.getHours()), pad(now.getMinutes()) ].join(":");

function pad(n: number) {
  return String(n).padStart(2, "0");
}

export const inputSchema: RJSFSchema = {
  type: "object",
  properties: {
    city: { 
      type: "string",
      title: "Ciudad",
    },
    total_transaction_amount: {
      type: "number",
      minimum: 1,
      multipleOf: 0.01,
      title: "Monto total",
      default: 1,
    },
    currency_type: { $ref: "#/definitions/CurrencyType" },
    claimed_transactions: {
      type: "array",
      title: "Transacciones",
      items: { type: "object", $ref: "#/definitions/Transaction" },
      minItems: 1,
    },
    measure_information: { 
      type: "object",
      title: "Información preliminar",
      $ref: "#/definitions/MeasureInformation",
    },
    claimant_partner: { 
      type: "object",
      title: "Identificación del involucrado",
      $ref: "#/definitions/ClaimantPartner",
    },
    claimant_request: { 
      type: "object",
      title: "Antecedentes",
      $ref: "#/definitions/ClaimantRequest",
    },
  },
  required: [
    "city",
    "total_transaction_amount",
    "currency_type",
    "claimed_transactions",
    "measure_information",
    "claimant_partner",
    "claimant_request",
  ],
  definitions: {
    MeasureInformation: {
      type: "object",
      required: ["communication_date"],
      properties: {
        local_police_number: {
          type: ["integer", "null"],
          minimum: 0,
          maximum: 999,
          title: "Nº juzgado de policía local",
          default: null,
        },
        communication_date: {
          type: "string",
          format: "date",
          title: "Fecha de comunicación al cliente",
          default: today,
        },
      },
    },
    Transaction: {
      type: "object",
      required: ["amount", "currency_type", "transaction_type", "transaction_datetime"],
      properties: {
        amount: {
          type: ["number", "null"],
          minimum: 1,
          multipleOf: 0.01,
          title: "Monto",
          default: null,
        },
        currency_type: { $ref: "#/definitions/CurrencyType" },
        transaction_type: {
          $ref: "#/definitions/TransactionType"
        },
        transaction_datetime: {
          type: "string",
          format: "date-time",
          title: "Fecha/hora",
          default: defaultDateTime,
        }
      },
    },
    Payment: {
      type: "object",
      required: ["amount", "currency_type"],
      properties: {
        amount: {
          type: ["number", "null"],
          minimum: 1,
          multipleOf: 0.01,
          title: "Monto del abono",
          default: null,
        },
        currency_type: { $ref: "#/definitions/CurrencyType" },
        subsequent_balance: {
          type: ["number", "null"],
          minimum: 1,
          multipleOf: 0.01,
          title: "Monto de saldo posterior",
          default: null,
        },
        payment_datetime: {
          type: "string",
          format: "date-time",
          title: "Fecha/hora del abono",
          default: defaultDateTime,
        }
      },
    },
    SecuritySystem: {
      type: "string",
      title: "Sistema de seguridad",
      enum: ["mastercard_connect", "safesigner", "celmedia"],
      default: "mastercard_connect",
    },
    SecurityMeasure: {
      type: "object",
      required: ["security_system"],
      properties: {
        security_system: {
          $ref: "#/definitions/SecuritySystem",
        },
        context: {
          type: ["string", "null"],
          title: "Contexto",
          default: null,
        },
        transaction_amount: {
          type: ["number", "null"],
          minimum: 1,
          multipleOf: 0.01,
          title: "Monto de transacción",
          default: null,
        },
        currency_type: {
          title: "Divisa",
          type: ["string", "null"],
          enum: ["clp", "usd", "uf", null],
          default: null,
        },
        transaction_date: {
          type: ["string", "null"],
          format: "date",
          title: "Fecha de transacción",
          default: null,
        },
      },
    },
    CurrencyType: {
      type: "string",
      title: "Divisa",
      enum: ["clp", "usd", "uf"],
      default: "clp",
    },
    Gender: {
      type: ["string", "null"],
      title: "Género",
      enum: ["male", "female", null],
      default: null,
    },
    TransactionType: {
      type: "string",
      title: "Tipo de transacción",
      enum: [
        "non_face_to_face_purchase",
        "bank_transfer",
        "atm_withdrawal",
        "in_person_purchase",
      ],
      default: "non_face_to_face_purchase",
    },
    ClaimantPartner: {
      type: "object",
      required: [
        "name",
        "rut",
        "crm_complaint",
        "has_more_complaints_due_ignorance_crm",
      ],
      properties: {
        name: { 
          type: "string",
          title: "Nombre",
        },
        rut: {
          type: "string",
          title: "Rut",
          pattern: RUT_PATTERN,
        },
        gender: { $ref: "#/definitions/Gender" },
        eibs_address: { 
          type: ["string", "null"],
          title: "Dirección E-IBS",
          default: null,
        },
        affidavit_address: { 
          type: ["string", "null"],
          title: "Dirección declaración Jurada",
          default: null,
        },
        complaint_address: { 
          type: ["string", "null"],
          title: "Dirección denuncio",
          default: null,
        },
        eibs_phone_number: { 
          type: ["string", "null"],
          title: "Nº teléfono E-IBS",
          default: null,
        },
        affidavit_phone_number: { 
          type: ["string", "null"],
          title: "Nº teléfono declaración Jurada",
          default: null,
        },
        complaint_phone_number: { 
          type: ["string", "null"],
          title: "Nº teléfono denuncio",
          default: null,
        },
        eibs_email: { 
          type: ["string", "null"],
          title: "E-mail E-IBS",
          default: null,
        },
        affidavit_email: { 
          type: ["string", "null"],
          title: "E-mail declaración Jurada",
          default: null,
        },
        complaint_email: { 
          type: ["string", "null"],
          title: "E-mail denuncio",
          default: null,
        },
        crm_complaint: { 
          type: "string",
          title: "Reclamo CRM",
        },
        has_more_complaints_due_ignorance_crm: { 
          type: ["boolean", "null"],
          title: "Posee más reclamos por desconocimiento (CRM)",
          default: false,
        },
      },
    },
    ClaimantRequest: {
      type: "object",
      required: [
        "affidavit_send_date",
        "complaint_datetime",
        "cca_report_exists",
        "valid_complaint_format",
      ],
      properties: {
        article_5_presumptions: {
          type: "array",
          title: "Presunciones del artículo 5 ter",
          items: {
            type: "string",
            enum: [
              "letter_b",
              "letter_c",
              "letter_d",
              "letter_g",
              "letter_h",
            ],
          },
          uniqueItems: true,
          default: [],
        },
        first_bank_account_box_interaction_date: {
          type: ["string", "null"],
          format: "date",
          title: "1era Interacción con casilla",
          default: null,
        },
        affidavit_send_date: {
          type: "string",
          format: "date",
          title: "Envío de declaración jurada",
          default: today,
        },
        complaint_send_date: {
          type: ["string", "null"],
          format: "date",
          title: "Envío de denuncia",
          default: null,
        },
        complaint_datetime: {
          type: "string",
          format: "date-time",
          title: "Fecha/hora denuncia",
          default: defaultDateTime,
        },
        payments: {
          type: "array",
          title: "Abonos",
          items: { type: "object", $ref: "#/definitions/Payment" },
        },
        security_measures: {
          type: "array",
          title: "Medidas de seguridad",
          maxItems: 3,
          items: { type: "object", $ref: "#/definitions/SecurityMeasure" },
        },
        valid_complaint_format: { 
          type: ["boolean", "null"],
          title: "Formato denuncia corresponde",
          default: false,
        },
        cca_report_exists: { 
          type: ["boolean", "null"],
          title: "Existe informe CCA",
          default: false,
        },
        lost_phone_date: { 
          type: ["string", "null"],
          title: "Fecha de extravío o robo de celular",
          format: "date",
          default: null,
        },
        lost_payment_card_date: { 
          type: ["string", "null"],
          title: "Fecha de extravío o robo de tarjeta",
          format: "date",
          default: null,
        },
      }
    },
  },
};

export const uiSchema = {
  "*": {
    "ui:options": {
      "autocomplete": "off",
    },
  },
  total_transaction_amount: {
    "ui:widget": "updown",
    "ui:options": {
      inputType: "number",
    },
  },
  currency_type: {
    "ui:enumNames": ["CLP", "USD", "UF"],
  },
  claimed_transactions: {
    items: {
      amount: {
        "ui:widget": "updown",
        "ui:options": {
          inputType: "number",
        },
      },
      transaction_type: {
        "ui:enumNames": [
          "Compra no presencial",
          "Transferencia bancaria",
          "Giro en cajero automático",
          "Compra presencial",
        ],
      },
      currency_type: {
        "ui:enumNames": ["CLP", "USD", "UF"],
      },
      transaction_datetime: {
        "ui:widget": "date-time",
        "yearsRange": [
          1980,
          2080,
        ],
        "format": "DMY",
      },
    },
  },
  measure_information: {
    communication_date: {
      "ui:widget": "date",
      "yearsRange": [
        1980,
        2080,
      ],
      "format": "DMY",
    },
    local_police_number: {
      "ui:widget": "updown",
    },
  },
  claimant_partner: {
    gender: {
      "ui:enumNames": ["Masculino", "Femenino", "No especificado"],
      "ui:widget": "radio",
    },
  },
  claimant_request: {
    article_5_presumptions: {
      "ui:widget": "checkboxes",
      "ui:enumNames": [
        "Letra b",
        "Letra c",
        "Letra d",
        "Letra g",
        "Letra h",
      ],
      "ui:options": {
        inline: true,
      },
    },
    affidavit_send_date: {
      "ui:widget": "date",
      "yearsRange": [
        1980,
        2080,
      ],
      "format": "DMY",
    },
    complaint_send_date: {
      "ui:widget": "date",
      "yearsRange": [
        1980,
        2080,
      ],
      "format": "DMY",
    },
    first_bank_account_box_interaction_date: {
      "ui:widget": "date",
      "yearsRange": [
        1980,
        2080,
      ],
      "format": "DMY",
    },
    complaint_datetime: {
      "ui:widget": "date-time",
      "yearsRange": [
        1980,
        2080,
      ],
      "format": "DMY",
    },
    security_measures: {
      items: {
        security_system: {
          "ui:enumNames": [
            "Mastercard Connect",
            "SafeSigner",
            "CELMEDIA",
          ],
        },
        transaction_amount: {
          "ui:widget": "updown",
          "ui:options": {
            inputType: "number",
          },
        },
        currency_type: {
          "ui:enumNames": ["CLP", "USD", "UF", "Sin divisa"],
        },
        transaction_date: {
          "ui:widget": "date",
          "yearsRange": [
            1980,
            2080,
          ],
          "format": "DMY",
        },
      },
    },
    payments: {
      items: {
        currency_type: {
          "ui:enumNames": ["CLP", "USD", "UF"],
        },
        subsequent_balance: {
          "ui:widget": "updown",
          "ui:options": {
            inputType: "number",
          },
        },
        amount: {
          "ui:widget": "updown",
          "ui:options": {
            inputType: "number",
          },
        },
        payment_datetime: {
          "ui:widget": "date-time",
          "yearsRange": [
            1980,
            2080,
          ],
          "format": "DMY",
        }
      }
    },
    lost_phone_date: {
      "ui:widget": "date",
      "yearsRange": [
        1980,
        2080,
      ],
      "format": "DMY",
    },
    lost_payment_card_date: {
      "ui:widget": "date",
      "yearsRange": [
        1980,
        2080,
      ],
      "format": "DMY",
    },
  },
};
