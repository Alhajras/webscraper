export interface Runner {
  collected_documents: number
  current_crawled_url: Record<string, string>
  completed_at: string,
  crawler: number,
  crawler_name: number,
  created_at: string,
  deleted: boolean,
  description: string,
  id: number,
  status: string,
  name: string,
  machine: string,
  statistics: Statistics
}

export interface Statistics {
  visited_pages: number
  average_docs_per_page: number
  average_processing_time: number
  avg_loading_time: number
  avg_page_size: number
  http_codes: Record<any, any>
}
