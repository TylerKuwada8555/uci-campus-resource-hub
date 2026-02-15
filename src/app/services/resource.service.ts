import { Injectable, inject } from '@angular/core';
import { Resource, UserProfile } from '../models/user.model';
import { AuthService } from './auth.service';
import { ApiService } from './api.service';
import resourceData from '../../../data/uci_resources.json';

@Injectable({
    providedIn: 'root'
})
export class ResourceService {
    private authService = inject(AuthService);
    private apiService = inject(ApiService)
    private allResources: Resource[] = resourceData as Resource[];

    getResources(): Resource[] {
        return this.allResources;
    }

    getRankedResources(): Resource[] {
        const user = this.authService.user();
        const resources = this.allResources.map(r => ({
            ...r,
            relevanceScore: 0,
            badges: this.generateBadges(r)
        }));

        if (!user) return resources;

        return this.rankByProfile(resources, user);
    }

    searchResources(query: string): Resource[] {
        if (!query.trim()) return this.getRankedResources();

        const lowerQuery = query.toLowerCase();
        return this.getRankedResources().filter(r =>
            r.name.toLowerCase().includes(lowerQuery) ||
            r.description.toLowerCase().includes(lowerQuery) ||
            r.category.toLowerCase().includes(lowerQuery) ||
            r.target_audience.toLowerCase().includes(lowerQuery)
        );
    }

    private rankByProfile(resources: Resource[], user: UserProfile): Resource[] {
        const scored = resources.map(resource => {
            let score = 0;

            // Major matching
            score += this.getMajorRelevance(resource, user.major);

            // Year matching
            score += this.getYearRelevance(resource, user.year);

            // International student matching
            if (user.isInternational) {
                score += this.getInternationalRelevance(resource);
            }

            // Category priority boost
            score += this.getCategoryBoost(resource, user);

            return { ...resource, relevanceScore: score };
        });

        return scored.sort((a, b) => (b.relevanceScore ?? 0) - (a.relevanceScore ?? 0));
    }

    private getMajorRelevance(resource: Resource, major: string): number {
        const majorLower = major.toLowerCase();
        const majorMappings: Record<string, string[]> = {
            'computer science': ['ics', 'information and computer sciences', 'engineering'],
            'informatics': ['ics', 'information and computer sciences'],
            'software engineering': ['ics', 'engineering', 'information and computer sciences'],
            'data science': ['ics', 'information and computer sciences'],
            'electrical engineering': ['engineering', 'samueli'],
            'mechanical engineering': ['engineering', 'samueli'],
            'civil engineering': ['engineering', 'samueli'],
            'biology': ['biological sciences', 'bio'],
            'chemistry': ['physical sciences'],
            'physics': ['physical sciences'],
            'mathematics': ['physical sciences'],
            'psychology': ['social sciences'],
            'economics': ['social sciences'],
            'political science': ['social sciences'],
            'business': ['merage', 'business'],
            'nursing': ['nursing'],
            'education': ['education'],
            'art': ['arts', 'claire trevor'],
            'humanities': ['humanities'],
            'public health': ['public health'],
            'social ecology': ['social ecology'],
            'pharmaceutical sciences': ['pharmacy', 'pharmaceutical'],
            'law': ['law'],
            'medicine': ['medicine'],
            'undeclared': ['undeclared']
        };

        const keywords = majorMappings[majorLower] || [majorLower];
        const text = (resource.name + ' ' + resource.target_audience + ' ' + resource.description).toLowerCase();

        for (const keyword of keywords) {
            if (text.includes(keyword)) return 30;
        }

        return 0;
    }

    private getYearRelevance(resource: Resource, year: string): number {
        const audience = resource.target_audience.toLowerCase();

        if (year === 'graduate' || year === 'phd') {
            if (audience.includes('graduate')) return 15;
        } else {
            if (audience.includes('undergraduate')) return 15;
        }

        // Resources for all students
        if (audience.includes('undergraduate and graduate')) return 10;

        return 0;
    }

    private getInternationalRelevance(resource: Resource): number {
        const text = (resource.name + ' ' + resource.description + ' ' + resource.target_audience).toLowerCase();
        if (text.includes('international') || text.includes('visa') || text.includes('f-1') || text.includes('j-1')) {
            return 40;
        }
        return 0;
    }

    private getCategoryBoost(resource: Resource, user: UserProfile): number {
        // Freshmen and sophomores may benefit more from basic needs / academic advising
        const earlyYears = ['freshman', '1st year', '2nd year', 'sophomore'];
        if (earlyYears.includes(user.year.toLowerCase())) {
            if (resource.category === 'academic' || resource.category === 'basic_needs') return 5;
        }
        // Seniors and grad students may benefit more from career
        const lateYears = ['senior', '4th year', 'graduate', 'phd'];
        if (lateYears.includes(user.year.toLowerCase())) {
            if (resource.category === 'career' || resource.category === 'financial') return 5;
        }
        return 0;
    }

    private generateBadges(resource: Resource): string[] {
        const badges: string[] = [];
        const now = new Date();
        const hour = now.getHours();
        const day = now.getDay();

        // simulate "open now" for weekday business hours
        if (day >= 1 && day <= 5 && hour >= 8 && hour < 17) {
            badges.push('Open Now');
        }

        // Category-specific badges
        if (resource.category === 'basic_needs') {
            badges.push('Essential');
        }
        if (resource.category === 'health') {
            if (resource.name.includes('Crisis')) {
                badges.push('24/7 Available');
            }
        }
        if (resource.category === 'financial') {
            badges.push('Deadline Approaching');
        }
        if (resource.category === 'career') {
            badges.push('Popular');
        }

        return badges;
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
