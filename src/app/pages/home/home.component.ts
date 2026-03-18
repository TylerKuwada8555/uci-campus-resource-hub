import { Component, inject, signal, computed } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { ResourceService } from '../../services/resource.service';
import { ResourceCardComponent } from '../../components/resource-card/resource-card.component';
import { Resource } from '../../models/user.model';
import { toSignal, toObservable } from '@angular/core/rxjs-interop';
import { debounceTime, distinctUntilChanged, startWith, switchMap } from 'rxjs';

@Component({
    selector: 'app-home',
    standalone: true,
    imports: [CommonModule, FormsModule, ResourceCardComponent],
    templateUrl: './home.component.html',
    styleUrl: './home.component.css'
})
export class HomeComponent {
    private authService = inject(AuthService);
    private resourceService = inject(ResourceService);
    private router = inject(Router);

    user = this.authService.user;

    searchQuery = signal('');
    isSearchFocused = signal(false);
    selectedCategory = signal<string | null>(null);
    resources = toSignal(
        toObservable(this.searchQuery).pipe(
            startWith(''),
            debounceTime(300),
            distinctUntilChanged(),
            switchMap(query => this.resourceService.searchResources(query))
        ),
        { initialValue: [] as Resource[] }
    );

    categories = [
        { key: null, label: 'All'},
        { key: 'basic_needs', label: 'Basic Needs'},
        { key: 'health', label: 'Health'},
        { key: 'academic', label: 'Academic'},
        { key: 'career', label: 'Career'},
        { key: 'financial', label: 'Financial'},
        { key: 'housing', label: 'Housing'},
        { key: 'accommodations', label: 'Accessibility'},
        { key: 'recreation', label: 'Recreation'}
    ];

    filteredResources = computed(() => {
        const category = this.selectedCategory();

        let resources = this.resources();

        if (category) {
            resources = resources.filter(r => r.category === category);
        }

        return resources;
    });

    showAllResources = signal(false);

    greeting = computed(() => {
        const name = this.user()?.name || 'Anteater';
        const hour = new Date().getHours();
        if (hour < 12) return `Good morning, ${name}`;
        if (hour < 17) return `Good afternoon, ${name}`;
        return `Good evening, ${name}`;
    });

    suggestion = computed(() => {
        const user = this.user();
        if (!user) return 'exploring campus resources?';

        const suggestions = [
            `checking out resources for ${user.major} students?`,
            'finding academic support near you?',
            'discovering what\'s available for you today?',
            'connecting with campus services?'
        ];
        return suggestions[Math.floor(Math.random() * suggestions.length)];
    });

    onSearch(query: string): void {
        this.searchQuery.set(query);
    }

    selectCategory(key: string | null): void {
        this.selectedCategory.set(key);
    }

    toggleShowAll(): void {
        this.showAllResources.update(v => !v);
    }

    trackByName(resource: Resource): string {
        return resource.name;
    }

    logout(): void {
        this.authService.logout();
        this.router.navigate(['/login']);
    }
}
