export interface GlossaryTerm {
  id: number;
  novel_id: number;
  original_term: string;
  preferred_term: string;
  term_type: string;
  context?: string;
  frequency: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface GlossaryTermCreate {
  novel_id: number;
  original_term: string;
  preferred_term: string;
  term_type: string;
  context?: string;
}

export interface GlossaryTermUpdate {
  preferred_term?: string;
  term_type?: string;
  context?: string;
  is_active?: boolean;
}

export interface BulkGlossaryImport {
  novel_id: number;
  terms: GlossaryTermImport[];
}

export interface GlossaryTermImport {
  original_term: string;
  preferred_term: string;
  term_type: string;
  context?: string;
}

export interface TermTypeInfo {
  [termType: string]: number;
}

export interface GlossaryExport {
  novel_title: string;
  novel_id: number;
  export_date: string;
  total_terms: number;
  terms: GlossaryTermExport[];
}

export interface GlossaryTermExport {
  original_term: string;
  preferred_term: string;
  term_type: string;
  context?: string;
  frequency: number;
}

export interface BulkImportResult {
  message: string;
  created_count: number;
  updated_count: number;
  total_processed: number;
  errors: string[];
} 