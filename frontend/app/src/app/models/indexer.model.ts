export interface Indexer {
  created_at: string,
  completed_at: string,
  id: number,
  deleted: boolean,
  name: number
  inspectors_to_be_indexed: number[],
  description: string,
  status: string,
}
