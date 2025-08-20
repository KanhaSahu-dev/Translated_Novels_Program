export interface Novel {
  id: number;
  title: string;
  url: string;
  description: string;
  author: string;
  status: string;
  total_chapters: number;
  chapters: Chapter[];
}

export interface Chapter {
  id: number;
  chapter_number: number;
  title: string;
  url: string;
  is_processed: boolean;
  word_count: number;
}

export interface ChapterContent {
  id: number;
  novel_id: number;
  chapter_number: number;
  title: string;
  url: string;
  original_content: string;
  refined_content?: string;
  is_processed: boolean;
  word_count: number;
  created_at: string;
  updated_at: string;
}

export interface NovelSearchResult {
  title: string;
  url: string;
  description: string;
}

export interface NovelSearchRequest {
  novel_name: string;
}

export interface ChapterExtractionRequest {
  novel_url: string;
  max_chapters?: number;
  use_selenium: boolean;
} 