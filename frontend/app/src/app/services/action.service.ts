import { Injectable } from '@angular/core';
import {ApiService} from "src/app/services/api.service";
import {Observable} from "rxjs";
import {HttpParams} from "@angular/common/http";
import {Action} from "src/app/models/action.model";

@Injectable({
  providedIn: 'root'
})
export class ActionService {


  private readonly endpointPath = 'actions/'

  public constructor(private readonly client: ApiService) {
  }

  public get(id: number): Observable<Action> {
    return this.client.get<Action>(`${this.endpointPath}${id}`)
  }

  public post(action: Partial<Action>): Observable<Action> {
    return this.client.post<Action>(`${this.endpointPath}`, action)
  }

  public update(id: number, action: Partial<Action>): Observable<Action> {
    return this.client.put<Action>(`${this.endpointPath}${id}/`, action)
  }

  public list(additionalParams = {}): Observable<Action[]> {
    const params = new HttpParams({fromObject: additionalParams})
    return this.client.getList<Action>(this.endpointPath, params)
  }

    public disableActionsChain(id: number): any {
    return this.client.post<Action>(`${this.endpointPath}${id}/disable-actions-chain/`, {id})
  }
}
