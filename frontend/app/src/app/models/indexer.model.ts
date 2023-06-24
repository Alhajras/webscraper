export interface Indexer {
  created_at: string,
  completed_at: string,
  id: number,
  deleted: boolean,
  name: string
  inspectors_to_be_indexed: number[],
  description: string,
  status: string,
  k_parameter: number,
  b_parameter: number,
  skip_words: string,
  small_words_threshold: number,
}
