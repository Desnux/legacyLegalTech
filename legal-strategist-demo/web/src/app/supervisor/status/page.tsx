"use client";

import classNames from "classnames";
import { useRouter } from "next/navigation";

// mock data
const cases: Case[] = [
  {
    id: "e69c0bd4-124d-45c6-bf34-36e086e02a0f",
    title: "BANCO CONSORCIO/VIA UNO CHILE SPA",
    legal_subject: 'promissory_note_collection',
    winner: null,
    status: 'active',
    created_at: "2025-01-10T12:12:58",
    latest_step: 'exceptions',
    court: "15º Juzgado Civil de Santiago",
    link: true,
  },
  {
    id: "49c16587-2620-443c-a45e-d350ea197d6c",
    title: "BANCO CONSORCIO/AUSTRAL TRADING SPA",
    legal_subject: 'promissory_note_collection',
    winner: null,
    status: 'active',
    created_at: "2024-01-21T17:12:58",
    latest_step: 'exceptions',
    court: "15º Juzgado Civil de Santiago",
  },
  {
    id: "37195bc0-1879-41d6-bfcb-c3a09fc400d2",
    title: "BANCO CONSORCIO/MF SA.",
    legal_subject: 'promissory_note_collection',
    winner: null,
    status: 'active',
    created_at: "2023-03-27T13:33:15",
    latest_step: 'exceptions_response',
    court: "11º Juzgado Civil de Santiago",
  },
  {
    id: "4a065f5a-6272-4267-bf0b-e918db3e618c",
    title: "BANCO CONSORCIO/SOCIEDAD INMOBILIARIA E INVERS",
    legal_subject: 'promissory_note_collection',
    winner: null,
    status: 'draft',
    created_at: "2024-12-17T09:50:05",
    latest_step: 'demand_start',
    court: "15º Juzgado Civil de Santiago",
  },
  {
    id: "c60e2309-b524-4762-97a2-9359c4455207",
    title: "BANCO CONSORCIO/COMERCIAL ULZURRUN Y CONTRERASLI",
    legal_subject: 'promissory_note_collection',
    winner: null,
    status: 'active',
    created_at: "2024-05-15T07:39:13",
    latest_step: 'exceptions',
    court: "21º Juzgado Civil de Santiago",
  },
  {
    id: "7b882679-3438-4aa9-af64-6481b556909d",
    title: "BANCO CONSORCIO/COMERCIAL J Y R LTDA",
    legal_subject: 'bill_collection',
    winner: null,
    status: 'active',
    created_at: "2023-12-06T19:12:29",
    latest_step: 'exceptions_response',
    court: "8º Juzgado Civil de Santiago",
  },
  {
    id: "1e352e50-f626-48bb-8690-80a70ea822d2",
    title: "BANCO CONSORCIO/TRANSPORTES GAMA SPA",
    legal_subject: 'promissory_note_collection',
    winner: 'plaintiffs',
    status: 'finished',
    created_at: "2023-09-20T15:15:43",
    latest_step: 'legal_sentence',
    court: "20º Juzgado Civil de Santiago",
  }
];

// translations
const translations: Record<string, string> = {
  promissory_note_collection: "Cobro de pagaré",
  bill_collection: "Cobro de factura",
  plaintiffs: "Ejecutantes",
  active: "Activo",
  draft: "Preparación",
  finished: "Terminado",
  demand_start: "Ingreso demanda",
  dispatch_resolution: "Resolución despáchese",
  legal_sentence: "Sentencia",
  exceptions: "Excepciones",
  exceptions_response: "Respuesta a excepciones"
};

const stepsOrder = [
  "demand_start",
  "dispatch_resolution",
  "exceptions",
  "exceptions_response",
  "hearing_call",
  "legal_sentence"
];

interface Case {
  id: string;
  title: string;
  legal_subject: string;
  winner: string | null;
  status: string;
  created_at: string;
  latest_step: string;
  court: string;
  link?: boolean;
}

const CaseProgress = ({ cases }: { cases: Case[] }) => {
  const router = useRouter();

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Estado de avance de los juicios</h1>
      <div className="grid grid-cols-1 gap-4">
        {cases.map((c) => (
          <div
            key={c.id}
            className={classNames(
              "border rounded-lg p-4 flex justify-between items-center bg-white shadow-md",
              c.link && "cursor-pointer",
            )}
            onClick={c.link ? () => router.push(`/case/${c.id}`) : undefined}
          >
            <div className="w-3/4">
              <h2 className="text-lg font-semibold">{c.title}</h2>
              <p>{translations[c.legal_subject]}</p>
              <p>{c.court}</p>
              <p>{c.winner && translations[c.winner]}</p>
              <p>{new Date(c.created_at).toLocaleDateString()}</p>
              <div className="mt-4 flex items-center">
                {stepsOrder.map((step, index) => (
                  <div
                    key={step}
                    className={`w-10 h-2 ${
                      index <= stepsOrder.indexOf(c.latest_step)
                        ? "bg-blue-600"
                        : "bg-gray-300"
                    } rounded-full mx-1`}
                  ></div>
                ))}
                <span className="ml-2">
                  {translations[c.latest_step] || c.latest_step}
                </span>
              </div>
            </div>
            <div className="w-1/4 text-right">
              <p className="text-xl font-bold">
                {translations[c.status] || c.status}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default function SupervisorStatusPage() {
  return <CaseProgress cases={cases} />;
}
