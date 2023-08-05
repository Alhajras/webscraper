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
}
