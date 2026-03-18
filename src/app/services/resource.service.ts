import { Injectable, inject } from '@angular/core';
import { Resource } from '../models/user.model';
import { AuthService } from './auth.service';
import { ApiService } from './api.service';
import { Observable, of } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class ResourceService {
    private authService = inject(AuthService);
    private apiService = inject(ApiService);

    searchResources(
        query: string
    ): Observable<Resource[]> {
        const user = this.authService.user();
        if (!query && !user) {
            return of([]);
        }
        
        const userName = user?.name;
        const userYear = user?.year;
        const userMajor = user?.major;
        const userDomestic = user ? !user.isInternational : false;

        return this.apiService.query(query, userName, userYear, userMajor, userDomestic);
    }

    getCategoryLabel(category: string): string {
        const labels: Record<string, string> = {
            'basic_needs': 'Basic Needs',
            'health': 'Health & Wellness',
            'accommodations': 'Accommodations',
            'career': 'Career',
            'financial': 'Financial Aid',
            'academic': 'Academic',
            'housing': 'Housing',
            'recreation': 'Recreation'
        };
        return labels[category] || category;
    }
}
