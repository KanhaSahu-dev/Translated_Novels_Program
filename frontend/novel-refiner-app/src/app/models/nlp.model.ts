export interface RefinementResult {
  original_text: string;
  refined_text: string;
  changes_made: Change[];
  confidence_score: number;
  processing_time: number;
}

export interface Change {
  type: string;
  description: string;
}

export interface RefineTextRequest {
  text: string;
  use_glossary: boolean;
  novel_id?: number;
}

export interface RefineChapterRequest {
  chapter_id: number;
  use_glossary: boolean;
}

export interface ChapterRefinementResponse {
  chapter_id: number;
  chapter_number: number;
  title: string;
  success: boolean;
  refinement_result?: RefinementResult;
  error_message?: string;
}

export interface BatchRefineRequest {
  novel_id: number;
  chapter_ids?: number[];
  use_glossary: boolean;
}

export interface ProcessingStatus {
  novel_id: number;
  novel_title: string;
  total_chapters: number;
  processed_chapters: number;
  completion_percentage: number;
  recent_logs: ProcessingLog[];
}

export interface ProcessingLog {
  chapter_id: number;
  processing_type: string;
  success: boolean;
  processing_time?: number;
  created_at: string;
}

export interface ContextAnalysis {
  novel_id: number;
  character_names: { [key: string]: EntityInfo };
  place_names: { [key: string]: EntityInfo };
  consistency_suggestions: ConsistencySuggestion[];
  total_unique_terms: number;
  chapters_analyzed: number;
}

export interface EntityInfo {
  canonical_form: string;
  variations: string[];
  frequency: number;
}

export interface ConsistencySuggestion {
  type: string;
  original_variations: string[];
  suggested_canonical: string;
  frequency: number;
} 