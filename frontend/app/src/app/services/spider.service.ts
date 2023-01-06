import {ApiService} from "src/app/services/api.service";
import {HttpParams} from "@angular/common/http";
import {Injectable} from '@angular/core';
import {Observable} from 'rxjs'
import {Spider} from "src/app/models/spider.model";

@Injectable({
  providedIn: 'root'
})
export class SpiderService {

  private readonly endpointPath = 'spiders/'

  public constructor(private readonly client: ApiService) {
  }

  public get(id: number): Observable<Spider> {
    return this.client.get<Spider>(`${this.endpointPath}${id}`)
  }

  public post(spider: Partial<Spider>): Observable<Spider> {
    return this.client.post<Spider>(`${this.endpointPath}`, spider)
  }

  public update(id: number, spider: Partial<Spider>): Observable<Spider> {
    return this.client.put<Spider>(`${this.endpointPath}${id}/`, spider)
  }

  public list(additionalParams = {}): Observable<Spider[]> {
    const params = new HttpParams({fromObject: additionalParams})
    return this.client.getList<Spider>(this.endpointPath, params)
  }
}
