import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Resource } from '../models/user.model';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})

export class ApiService {
  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  query(query_term: any, user_name:any, user_year: any, user_major: any, user_domestic: boolean): Observable<Resource[]> {
    return this.http.post<Resource[]>(`${this.baseUrl}/query`, {
      query: query_term,
      name: user_name,
      year: user_year,
      major: user_major,
      domestic: user_domestic
    }
    );
  }
}