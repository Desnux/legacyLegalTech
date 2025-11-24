export interface FoliosResponse {
    items:       Folio[];
    total:       number;
    offset:      number;
    limit:       number;
    total_pages: number;
    has_next:    boolean;
    has_prev:    boolean;
}

export interface Folio {
    id:                    number;
    folio:                 number;
    case_number:           number;
    year:                  number;
    doc:                   string;
    stage:                 string;
    procedure:             string;
    procedure_description: string;
    procedure_date:        Date;
    page:                  number;
    milestone:             string | null;
    created_at:            Date;
    updated_at:            Date;
    is_active:             boolean;
    scraping_session_id:   string;
    scraping_type:         string;
}