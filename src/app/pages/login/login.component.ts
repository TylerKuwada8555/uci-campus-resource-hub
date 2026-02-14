import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './login.component.html',
    styleUrl: './login.component.css'
})
export class LoginComponent {
    private router = inject(Router);
    private authService = inject(AuthService);

    isLoading = false;

    onSignIn(): void {
        this.isLoading = true;

        // Simulate sign-in delay
        setTimeout(() => {
            if (this.authService.hasProfile()) {
                // Returning user: redirect to main
                this.authService.login();
                this.router.navigate(['/home']);
            } else {
                // New user: collect data
                this.router.navigate(['/onboarding']);
            }
            this.isLoading = false;
        }, 800);
    }
}
