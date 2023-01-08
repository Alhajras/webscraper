export interface Runner {
  id: number,
  description: string,
  created_at: string,
  completed_at: string,
  deleted: boolean,
  spider: number,
  status: string,
}
