import { RJSFSchema } from "@rjsf/utils";

const RUT_PATTERN = "^(\\d{1,2}\\.\\d{3}\\.\\d{3}-[\\dkK])$";

export const inputSchema: RJSFSchema = {
  type: "object",
  properties: {
    plaintiff: { 
      type: "object",
      title: "Ejecutante",
      $ref: "#/definitions/Plaintiff",
    },
    legal_representatives: {
      type: "array",
      title: "Representantes legales del ejecutante",
      items: { type: "object", $ref: "#/definitions/LegalRepresentative" },
    },
    sponsoring_attorneys: {
      type: "array",
      title: "Abogados patrocinantes",
      items: { type: "object", $ref: "#/definitions/Attorney" },
    },
    creditors: {
      type: "array",
      title: "Acreedores",
      items: { type: "object", $ref: "#/definitions/Creditor" },
    },
    defendants: {
      type: "array",
      title: "Ejecutados",
      items: { type: "object", $ref: "#/definitions/Defendant" },
    },
    amount: { type: "integer", minimum: 0, title: "Monto en disputa", default: 0 },
    amount_currency: { $ref: "#/definitions/CurrencyType" },
    city: { type: "string", title: "Ciudad" },
    legal_subject: {
      type: "string",
      title: "Materia legal",
      enum: ["promisory_note_collection", "bill_collection", "general_collection"],
      default: "general_collection",
    },
    main_request: { type: "string", title: "Ruega" },
    documents: {
      type: "array",
      title: "Documentos",
      items: { type: "object", $ref: "#/definitions/Document" },
    },
    reasons_per_document: {
      type: "array",
      title: "Razones por documento",
      items: { type: "object", $ref: "#/definitions/Reason" },
    },
  },
  required: ["amount", "amount_currency", "city", "main_request", "plaintiff", "legal_subject"],
  definitions: {
    Attorney: {
      type: "object",
      required: ["name", "identifier"],
      properties: {
        name: { type: "string", title: "Nombre" },
        identifier: { type: "string", title: "RUT", pattern: RUT_PATTERN },
        address: { type: ["string", "null"], title: "Dirección", default: null },
      },
    },
    Creditor: {
      type: "object",
      required: ["name", "identifier"],
      properties: {
        name: { type: "string", title: "Nombre" },
        identifier: { type: "string", title: "RUT", pattern: RUT_PATTERN },
      },
    },
    CurrencyType: {
      type: "string",
      title: "Tipo de divisa",
      enum: ["clp", "usd", "uf"],
      default: "clp",
    },
    Defendant: {
      type: "object",
      required: ["name", "identifier", "type"],
      properties: {
        name: { type: "string", title: "Nombre" },
        identifier: { type: "string", title: "RUT", pattern: RUT_PATTERN },
        type: {
          type: "string",
          title: "Tipo",
          enum: ["debtor", "co_debtor"],
          default: "debtor",
        },
        address: { type: ["string", "null"], title: "Dirección" },
        occupation: { type: ["string", "null"], title: "Ocupación" },
        legal_representatives: {
          type: ["array", "null"],
          title: "Representantes legales",
          items: { type: "object", $ref: "#/definitions/LegalRepresentative" },
        },
      },
    },
    Document: {
      type: "object",
      required: ["identifier", "amount", "amount_currency"],
      properties: {
        identifier: { type: "string", title: "Identificador" },
        amount: { type: "integer", minimum: 0, title: "Monto a pagar", default: 0 },
        amount_currency: { $ref: "#/definitions/CurrencyType" },
      },
    },
    LegalRepresentative: {
      type: "object",
      required: ["name", "identifier"],
      properties: {
        name: { type: "string", title: "Nombre" },
        identifier: { type: "string", title: "RUT", pattern: RUT_PATTERN },
        address: { type: ["string", "null"], title: "Dirección" },
        occupation: { type: ["string", "null"], title: "Ocupación" },
      },
    },
    Plaintiff: {
      type: "object",
      required: ["name", "identifier"],
      properties: {
        name: { type: "string", title: "Nombre" },
        identifier: { type: "string", title: "RUT", pattern: RUT_PATTERN },
      },
    },
    Reason: {
      type: "object",
      required: ["reason"],
      properties: {
        reason: { type: "string", title: "Razón" },
        pending_amount: { type: "integer", minimum: 0, title: "Suma" },
        capital_amount: { type: "integer", minimum: 0, title: "Capital" },
        interest_amount: { type: "integer", minimum: 0, title: "Interés" },
        debt_amount: { type: "integer", minimum: 0, title: "Mora" },
      },
    },
  },
};

export const uiSchema = {
  "*": {
    "ui:options": {
      "autocomplete": "off",
    },
  },
  amount: {
    "ui:widget": "updown",
    "ui:options": {
      inputType: "number",
    },
  },
  amount_currency: {
    "ui:enumNames": ["CLP", "USD", "UF"],
  },
  main_request: {
    "ui:widget": "textarea",
  },
  defendants: {
    items: {
      type: {
        "ui:enumNames": ["Deudor", "Codeudor"],
      },
    },
  },
  documents: {
    "ui:options": {
      addable: false,
      removable: false,
      orderable: false,
    },
    items: {
      amount_currency: {
        "ui:enumNames": ["CLP", "USD", "UF"],
      },
    },
  },
  legal_subject: {
    "ui:enumNames": ["Pagaré, Cobro De", "Factura, Cobro De", "Obligación De Dar, Cumplimiento"],
  },
  reasons_per_document: {
    "ui:options": {
      addable: false,
      removable: false,
      orderable: false,
    },
  },
};
