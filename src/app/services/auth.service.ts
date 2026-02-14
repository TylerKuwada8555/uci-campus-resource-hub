import { Injectable, signal, computed } from '@angular/core';
import { UserProfile } from '../models/user.model';

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private readonly STORAGE_KEY = 'campus_hub_user';

    private userProfile = signal<UserProfile | null>(this.loadFromStorage());
    private isLoggedIn = signal<boolean>(this.loadFromStorage() !== null);

    readonly user = this.userProfile.asReadonly();
    readonly loggedIn = this.isLoggedIn.asReadonly();
    readonly hasProfile = computed(() => this.userProfile() !== null);

    login(): void {
        this.isLoggedIn.set(true);
    }

    setProfile(profile: UserProfile): void {
        this.userProfile.set(profile);
        this.isLoggedIn.set(true);
        this.saveToStorage(profile);
    }

    logout(): void {
        this.userProfile.set(null);
        this.isLoggedIn.set(false);
        localStorage.removeItem(this.STORAGE_KEY);
    }

    private loadFromStorage(): UserProfile | null {
        try {
            const data = localStorage.getItem(this.STORAGE_KEY);
            return data ? JSON.parse(data) : null;
        } catch {
            return null;
        }
    }

    private saveToStorage(profile: UserProfile): void {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(profile));
    }
}
