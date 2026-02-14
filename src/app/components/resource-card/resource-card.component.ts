import { Component, Input, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Resource } from '../../models/user.model';
import { ResourceService } from '../../services/resource.service';

@Component({
    selector: 'app-resource-card',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './resource-card.component.html',
    styleUrl: './resource-card.component.css'
})
export class ResourceCardComponent {
    @Input({ required: true }) resource!: Resource;

    private resourceService = inject(ResourceService);
    isExpanded = false;

    get categoryLabel(): string {
        return this.resourceService.getCategoryLabel(this.resource.category);
    }

    get categoryIcon(): string {
        return this.resourceService.getCategoryIcon(this.resource.category);
    }

    toggleExpand(): void {
        this.isExpanded = !this.isExpanded;
    }

    openResource(): void {
        window.open(this.resource.source_url, '_blank', 'noopener');
    }
}
