//ATUH
export interface RecepthorLoginRequest {
    captchaToken: string;
    email: string;
    password: string;
    skipCaptchaToken: string;
}

export interface RecepthorLoginResponse {
        expiresIn: string;
        token: string;
        user: RecepthorUser;
}

export interface RecepthorUser {
    email: string;
    id: string;
    role: string;
}

export interface RecepthorLoginErrorResponse {
    error: RecepthorLoginError;
    success: boolean;
}

interface RecepthorLoginError extends ErrorResponse {
    details: RecepthorLoginErrorDetails;
}

interface RecepthorLoginErrorDetails {
    field: string;
    issue: string;
}



//ERROR RESPONSE
export interface ErrorResponse {
    error: ErrorResponseData;
    success: boolean;
}

interface ErrorResponseData {
    message: string;
    name: string;
    statusCode: number;
}




//RECEPTORS
export interface ReceptorsResponse {
    pagination: Pagination;
    results: Receptor[];
}

export interface Pagination {
    currentPage:  number;
    pageSize:     number;
    totalPages:   number;
    totalRecords: number;
}

export interface Receptor {
    address: string;
    id: string;
    name: string;
    primaryEmail: string;
    primaryPhone: string;
    profiles: Profile[];
    secondaryEmail: string;
    secondaryPhone: string;
    user: User;
}

export interface Profile {
    tribunalId: string;
    tribunalName: string;
}

export interface User {
    firstName: string;
    id: string;
    lastName: string;
}

//TASKS
export interface CreateTaskRequest {
    address: string;
    addressDetails?: string;
    caseId: string;
    commune?: string;
    deadline: string;
    notes: string;
    receptorIds: string[];
    region?: string;
}

export interface Task {
    address: string;
    addressDetails: string;
    commune: string;
    deadline: string;
    id: string;
    notes: string;
    region: string;
    status: string;
    updatedAt: string;
}


export interface ListTasksResponse {
    pagination: Pagination;
    results:    Tasks[];
}

export interface Tasks {
    address:        string;
    addressDetails: string;
    commune:        string;
    createdAt:      string;
    deadline:       string;
    firmCase:       FirmCase;
    id:             string;
    notes:          string;
    quotes:         Quote[];
    region:         string;
    status:         string;
    summary:        null;
    updatedAt:      Date;
}

export interface FirmCase {
    addedByUser: User;
    case:        Case;
    firm:        Firm;
    id:          string;
}

export interface User {
    email?:    string;
    firstName: string;
    id:        string;
    lastName:  string;
}

export interface Case {
    bookType:   string;
    competence: string;
    id:         string;
    rol:        string;
    title:      string;
    tribunal:   Tribunal;
    year:       string;
}

export interface Tribunal {
    court: Firm;
    id:    string;
    name:  string;
}

export interface Firm {
    id:   string;
    name: string;
}
    
export interface Quote {
    createdAt:   Date;
    dateOffered: Date;
    id:          string;
    price:       number | null;
    receptor:    QuoteReceptor;
    status:      string;
    updatedAt:   Date;
}

export interface QuoteReceptor {
    id:           string;
    primaryEmail: string;
    user:         User;
}

export interface SearchAndAssignCaseRequest {
    bookType: string;
    competence: string;
    court: string;
    rol: string;
    tribunalCode: string;
    year: string;
}


export interface AssignCaseResponse {
    addedByUser: AddedByUser;
    case:        RecepthorCase;
    firmCaseId:  string;
    tribunal:    RecepthorTribunal;
    year:        string;
}

export interface AddedByUser {
    email: string;
    id:    string;
    name:  string;
}

export interface RecepthorCase {
    administrativeStatus: string;
    admissionDate:        Date;
    bookType:             string;
    caseStage:            string;
    competence:           string;
    history:              History[];
    id:                   string;
    legalStatus:          string;
    location:             string;
    procedure:            string;
    rol:                  string;
    title:                string;
}

export interface History {
    createdAt:   Date;
    date:        string;
    description: string;
    folio:       string;
    id:          string;
    name:        string;
    pageNumber:  string;
    stage:       string;
    updatedAt:   Date;
}

export interface RecepthorTribunal {
    court: RecepthorCourt;
    id:    string;
    name:  string;
}

export interface RecepthorCourt {
    id:   string;
    name: string;
}
