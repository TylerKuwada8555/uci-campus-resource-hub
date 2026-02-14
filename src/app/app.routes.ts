import { Routes } from '@angular/router';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './services/auth.service';

export const routes: Routes = [
    {
        path: 'login',
        loadComponent: () => import('./pages/login/login.component').then(m => m.LoginComponent)
    },
    {
        path: 'onboarding',
        loadComponent: () => import('./pages/onboarding/onboarding.component').then(m => m.OnboardingComponent)
    },
    {
        path: 'home',
        loadComponent: () => import('./pages/home/home.component').then(m => m.HomeComponent),
        canActivate: [() => {
            const authService = inject(AuthService);
            const router = inject(Router);
            if (authService.hasProfile()) {
                return true;
            }
            router.navigate(['/login']);
            return false;
        }]
    },
    {
        path: '',
        redirectTo: 'login',
        pathMatch: 'full'
    },
    {
        path: '**',
        redirectTo: 'login'
    }
];
