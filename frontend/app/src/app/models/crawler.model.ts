export interface Crawler {
  id: number,
  name: string,
  seed_url: string,
  description: string,
  created_at: string,
  deleted: boolean,
  template: number,
  threads: number,
  retry: number,
  sleep: number,
  timeout: number
  max_pages: number,
  max_depth:number,
  robot_file_url:string
  excluded_urls:string
}
