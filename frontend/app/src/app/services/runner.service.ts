import {Injectable} from '@angular/core';
import {ApiService} from "src/app/services/api.service";
import {Observable} from "rxjs";
import {HttpParams} from "@angular/common/http";
import {Runner} from "src/app/models/runner.model";

@Injectable({
  providedIn: 'root'
})
export class RunnerService {

  private readonly endpointPath = 'runners/'

  public constructor(private readonly client: ApiService) {
  }

  public get(id: number): Observable<Runner> {
    return this.client.get<Runner>(`${this.endpointPath}${id}`)
  }

  public post(runner: Partial<Runner>): Observable<Runner> {
    return this.client.post<Runner>(`${this.endpointPath}`, runner)
  }

  public start(runner: Partial<Runner>): Observable<Runner> {
    return this.client.post<Runner>(`${this.endpointPath}submit/`, runner)
  }

    public reStart(runner: Partial<Runner>): Observable<Runner> {
    return this.client.post<Runner>(`${this.endpointPath}start/`, runner)
  }

  public update(id: number, runner: Partial<Runner>): Observable<Runner> {
    return this.client.put<Runner>(`${this.endpointPath}${id}/`, runner)
  }

    public stop(id: number, runner: Partial<Runner>): Observable<Runner> {
    return this.client.post<Runner>(`${this.endpointPath}${id}/stop/`, runner)
  }


  public list(additionalParams = {}): Observable<Runner[]> {
    const params = new HttpParams({fromObject: additionalParams})
    return this.client.getList<Runner>(this.endpointPath, params)
  }
}
