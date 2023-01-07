import {Injectable} from '@angular/core';
import {ApiService} from "src/app/services/api.service";
import {Observable} from "rxjs";
import {HttpParams} from "@angular/common/http";
import {Template} from "src/app/models/template.model";

@Injectable({
  providedIn: 'root'
})
export class TemplateService {

  private readonly endpointPath = 'templates/'

  public constructor(private readonly client: ApiService) {
  }

  public get(id: number): Observable<Template> {
    return this.client.get<Template>(`${this.endpointPath}${id}`)
  }

  public post(template: Partial<Template>): Observable<Template> {
    return this.client.post<Template>(`${this.endpointPath}`, template)
  }

  public update(id: number, template: Partial<Template>): Observable<Template> {
    return this.client.put<Template>(`${this.endpointPath}${id}/`, template)
  }

  public list(additionalParams = {}): Observable<Template[]> {
    const params = new HttpParams({fromObject: additionalParams})
    return this.client.getList<Template>(this.endpointPath, params)
  }
}
