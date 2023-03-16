import {ApiService} from "src/app/services/api.service";
import {HttpParams} from "@angular/common/http";
import {Injectable} from '@angular/core';
import {Observable} from 'rxjs'
import {Crawler} from "src/app/models/crawler.model";

@Injectable({
  providedIn: 'root'
})
export class CrawlerService {

  private readonly endpointPath = 'crawlers/'

  public constructor(private readonly client: ApiService) {
  }

  public get(id: number): Observable<Crawler> {
    return this.client.get<Crawler>(`${this.endpointPath}${id}`)
  }

  public post(crawler: Partial<Crawler>): Observable<Crawler> {
    return this.client.post<Crawler>(`${this.endpointPath}`, crawler)
  }

  public update(id: number, crawler: Partial<Crawler>): Observable<Crawler> {
    return this.client.put<Crawler>(`${this.endpointPath}${id}/`, crawler)
  }

  public list(additionalParams = {}): Observable<Crawler[]> {
    const params = new HttpParams({fromObject: additionalParams})
    return this.client.getList<Crawler>(this.endpointPath, params)
  }
}
