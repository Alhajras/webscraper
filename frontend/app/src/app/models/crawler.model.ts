export interface Crawler {
  id: number,
  name: string,
  seed_url: string,
  description: string,
  created_at: string,
  completed_at: string,
  deleted: boolean,
  template: number,
}
