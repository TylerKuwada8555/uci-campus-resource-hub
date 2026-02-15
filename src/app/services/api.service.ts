import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Resource, UserProfile } from '../models/user.model';
import { AuthService } from './auth.service';

@Injectable({
    providedIn: 'root'
})

export class ApiService {
  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  query(query_term: any) {
    return this.http.get(`${this.baseUrl}/query`, query_term);
  }

  login(user_name:any, user_year: number, user_major: any, user_domestic: boolean) {
    return this.http.post(`${this.baseUrl}/login`, {
      name: user_name,
      year: user_year,
      major: user_major,
      domestic: user_domestic
    }
    );
  }
}