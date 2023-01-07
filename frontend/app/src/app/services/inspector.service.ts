import { Injectable } from '@angular/core';
import {ApiService} from "src/app/services/api.service";
import {Observable} from "rxjs";
import {HttpParams} from "@angular/common/http";
import {Inspector} from "src/app/models/inspector.model";

@Injectable({
  providedIn: 'root'
})
export class InspectorService {


  private readonly endpointPath = 'inspector/'

  public constructor(private readonly client: ApiService) {
  }

  public get(id: number): Observable<Inspector> {
    return this.client.get<Inspector>(`${this.endpointPath}${id}`)
  }

  public post(inspector: Partial<Inspector>): Observable<Inspector> {
    return this.client.post<Inspector>(`${this.endpointPath}`, inspector)
  }

  public update(id: number, inspector: Partial<Inspector>): Observable<Inspector> {
    return this.client.put<Inspector>(`${this.endpointPath}${id}/`, inspector)
  }

  public list(additionalParams = {}): Observable<Inspector[]> {
    const params = new HttpParams({fromObject: additionalParams})
    return this.client.getList<Inspector>(this.endpointPath, params)
  }
}
