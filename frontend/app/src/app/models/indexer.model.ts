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
  dictionary: string,
  q_gram_use_synonym: boolean,
  q_gram_q: number,
  skip_words: string,
  small_words_threshold: number,
}
