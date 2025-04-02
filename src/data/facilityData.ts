import { Facility, FacilityField } from '../types/facility';

export const facilityTypes = [
  'Term Loan',
  'Revolving Credit',
  'Bridge Loan',
  'Commercial Paper'
];

export const facilities: Facility[] = [
  {
    id: '1',
    name: 'Facility A',
    type: 'Term Loan',
    amount: '$5,000,000',
    rate: '4.25%',
    maturityDate: '2030-05-15',
    isActive: true
  },
  // ... other facilities
];

export const getFacilityFields = (facility: Facility): FacilityField[] => [
  {
    label: 'Facility Name',
    id: 'facility-name',
    value: facility.name
  },
  {
    label: 'Type',
    id: 'facility-type',
    type: 'select',
    value: facility.type,
    options: facilityTypes
  },
  {
    label: 'Amount',
    id: 'facility-amount',
    value: facility.amount
  },
  {
    label: 'Rate',
    id: 'facility-rate',
    value: facility.rate
  },
  {
    label: 'Maturity Date',
    id: 'maturity-date',
    type: 'date',
    value: facility.maturityDate
  }
]; 