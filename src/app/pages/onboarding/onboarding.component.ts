import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { UserProfile } from '../../models/user.model';

@Component({
    selector: 'app-onboarding',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './onboarding.component.html',
    styleUrl: './onboarding.component.css'
})
export class OnboardingComponent {
    private router = inject(Router);
    private authService = inject(AuthService);

    profile: UserProfile = {
        name: '',
        major: '',
        year: '',
        isInternational: false
    };

    majors: string[] = [
        'Computer Science',
        'Informatics',
        'Software Engineering',
        'Data Science',
        'Electrical Engineering',
        'Mechanical Engineering',
        'Civil Engineering',
        'Biology',
        'Chemistry',
        'Physics',
        'Mathematics',
        'Psychology',
        'Economics',
        'Political Science',
        'Business',
        'Nursing',
        'Education',
        'Art',
        'Humanities',
        'Public Health',
        'Social Ecology',
        'Pharmaceutical Sciences',
        'Law',
        'Medicine',
        'Undeclared'
    ];

    years: string[] = [
        'Freshman',
        'Sophomore',
        'Junior',
        'Senior',
        'Graduate',
        'PhD'
    ];

    isSubmitting = false;
    currentStep = 1;

    get isFormValid(): boolean {
        return this.profile.name.trim() !== '' &&
            this.profile.major !== '' &&
            this.profile.year !== '';
    }

    nextStep(): void {
        if (this.currentStep < 3) {
            this.currentStep++;
        }
    }

    prevStep(): void {
        if (this.currentStep > 1) {
            this.currentStep--;
        }
    }

    onSubmit(): void {
        if (!this.isFormValid) return;

        this.isSubmitting = true;

        setTimeout(() => {
            this.authService.setProfile(this.profile);
            this.router.navigate(['/home']);
        }, 600);
    }
}
