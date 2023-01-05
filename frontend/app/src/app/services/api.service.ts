import { HttpClient, HttpParams } from '@angular/common/http'
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs'
import { finalize, shareReplay } from 'rxjs/operators'

const PAGE_SIZE = 25
export const PAGE_SIZE_PARAM = 'limit'
export const PAGE_SIZE_NO_LIMIT = 'all'

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  private readonly baseUrl: string = '/api/'

  private readonly pendingGetRequests: Record<string, Observable<any>> = {}
  public constructor (private readonly httpClient: HttpClient) {}

  public request<T> (method: string, path: string, params?: HttpParams, body?: any): Observable<T> {
    const request$ = this.httpClient.request<T>(method, this.baseUrl + path, { body, withCredentials: true, params })

    if (method !== 'GET') {
      return request$
    }
    let pendingRequestId = path
    if (params != null) {
      const paramKeys = params.keys()
      paramKeys.sort()

      const sortedParams = paramKeys.map(key => `${key}=${String(params.getAll(key)?.join(','))}`)
      pendingRequestId += '?' + sortedParams.join('&')
    }
    if (this.pendingGetRequests[pendingRequestId] == null) {
      this.pendingGetRequests[pendingRequestId] = request$.pipe(
        finalize(() => delete this.pendingGetRequests[pendingRequestId]),
        shareReplay(1),
      )
    }
    return this.pendingGetRequests[pendingRequestId]
  }

  public getList<T> (path: string, params: HttpParams = new HttpParams()): Observable<T[]> {
    if (!params.has(PAGE_SIZE_PARAM)) {
      params = params.set(PAGE_SIZE_PARAM, PAGE_SIZE)
    }
    return this.get(path, params)
  }

  public get<T> (path: string, params?: HttpParams): Observable<T> {
    return this.request<T>('GET', path, params)
  }

  public post<T> (path: string, body?: any): Observable<T> {
    return this.request<T>('POST', path, undefined, body)
  }

  public put<T> (path: string, body?: any): Observable<T> {
    return this.request<T>('PUT', path, undefined, body)
  }

  public patch<T> (path: string, body?: any): Observable<T> {
    return this.request<T>('PATCH', path, undefined, body)
  }

  public delete<T> (path: string, body?: any, params?: HttpParams): Observable<T> {
    return this.request<T>('DELETE', path, params, body)
  }
}
