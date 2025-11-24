import { Participant, ParticipantRole } from "@/types/demand-text";
import { v4 as uuidv4 } from "uuid";

export const PARTICIPANT_TYPES = [
    { value: 'plaintiff', label: 'Demandante/Ejecutante (DTE)' },
    { value: 'sponsoring_attorney', label: 'Abogado demandante (Ab.DTE)' },
    { value: 'plaintiff_legal_representative', label: 'Representante Legal Demandante' },
    { value: 'defendant', label: 'Demandado/Ejecutado (DDO)' },
    { value: 'legal_representative', label: 'Representante Legal (AP.DDO)' },
    { value: 'guarantee', label: 'Demandado/Ejecutado (Aval)' },
  ] as const;
  
  export const SELECTABLE_PARTICIPANT_TYPES = [
    { value: 'defendant', label: 'Demandado/Ejecutado (DDO)' },
    { value: 'legal_representative', label: 'Representante Legal (AP.DDO)' },
    { value: 'guarantee', label: 'Demandado/Ejecutado II (Aval)' },
  ] as const;
  
  export const DEFAULT_PARTICIPANTS: Participant[] = [
    {
      id: uuidv4(),
      name: 'Banco Consorcio',
      dni: '99.500.410-0',
      address: 'AV. EL BOSQUE SUR 130 PISO 7, LAS CONDES, SANTIAGO',
      role: ParticipantRole.PLAINTIFF
    },
    {
      id: uuidv4(),
      name: 'Francisco Ignacio Ossa Guzman',
      dni: '7.771.373-5',
      address: 'AV. EL BOSQUE SUR 130 PISO 7, LAS CONDES, SANTIAGO',
      role: ParticipantRole.PLAINTIFF_LEGAL_REPRESENTATIVE
    },
    {
      id: uuidv4(),
      name: 'Raimundo Echeverría',
      dni: '19.640.102-4',
      address: 'Av. Providencia 1208, Santiago, Chile',
      role: ParticipantRole.SPONSORING_ATTORNEY
    }
  ];
