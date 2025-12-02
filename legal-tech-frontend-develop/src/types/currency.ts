const CURRENCY_TYPES = ["clp", "usd", "uf"] as const;

export type CurrencyType = typeof CURRENCY_TYPES[number];
