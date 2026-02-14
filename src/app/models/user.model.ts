export interface UserProfile {
    name: string;
    major: string;
    year: string;
    isInternational: boolean;
}

export interface Resource {
    category: string;
    name: string;
    location: string;
    contact_info: string;
    description: string;
    target_audience: string;
    source_url: string;
    // Computed properties for display
    relevanceScore?: number;
    badges?: string[];
}
