import {Injectable} from '@angular/core';
import {ApiService} from "src/app/services/api.service";
import {Observable} from "rxjs";
import {HttpParams} from "@angular/common/http";
import {Indexer} from "src/app/models/indexer.model";

@Injectable({
  providedIn: 'root'
})
export class IndexerService {

  private readonly endpointPath = 'indexers/'

  public constructor(private readonly client: ApiService) {
  }

  public get(id: number): Observable<Indexer> {
    return this.client.get<Indexer>(`${this.endpointPath}${id}`)
  }

  public post(indexer: Partial<Indexer>): Observable<Indexer> {
    return this.client.post<Indexer>(`${this.endpointPath}`, indexer)
  }

  public update(id: number, indexer: Partial<Indexer>): Observable<Indexer> {
    return this.client.put<Indexer>(`${this.endpointPath}${id}/`, indexer)
  }

  public list(additionalParams = {}): Observable<Indexer[]> {
    const params = new HttpParams({fromObject: additionalParams})
    return this.client.getList<Indexer>(this.endpointPath, params)
  }
}
