export const translatedLegalSubjects: Record<string, string> = {
    promissory_note_collection: "Cobro de pagaré",
    bill_collection: "Cobro de factura",
    general_collection: "Cumplimiento obligación de dar",
};

export const statusLabels: Record<string, string> = {
    draft: "Borrador",
    active: "Activo",
    archived: "Archivado",
    finished: "Finalizado",
};

export const statusColors: Record<string, string> = {
    draft: "bg-yellow-100 text-yellow-800",
    active: "bg-blue-100 text-blue-800",
    archived: "bg-gray-100 text-gray-800",
    finished: "bg-green-100 text-green-800",
};

export const partyLabels: Record<"plaintiffs" | "defendants" | "court" | "external_party", string> = {
    plaintiffs: "Abogado",
    defendants: "Ejecutado",
    court: "Juez",
    external_party: "Terceros",
};

export const partyRoles: Record<string, string> = {
    plaintiff: "Demandante",
    sponsoring_attorney: "Abogado demandante",
    plaintiff_legal_representative: "Representante legal demandante",
    defendant: "Ejecutado",
    legal_representative: "Representante legal",
    guarantee: "Aval",
    court: "Tribunal",
    external_party: "Tercero",
    defendant_attorney: "Abogado ejecutado",
};