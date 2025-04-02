export interface FacilityField {
  label: string;
  id: string;
  type?: 'text' | 'date' | 'select';
  value?: string;
  options?: string[];
}

export interface Facility {
  id: string;
  name: string;
  type: string;
  amount: string;
  rate: string;
  maturityDate: string;
  isActive?: boolean;
} 