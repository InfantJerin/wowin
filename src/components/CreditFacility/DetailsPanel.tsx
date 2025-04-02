import React, { useState, useEffect, ChangeEvent } from 'react';
import { getFacilityFields, facilityTypes } from '../../data/facilityData';
import type { Facility } from '../../types/facility';

interface DetailsPanelProps {
  facility: Facility | null;
  isNew?: boolean;
  onSave: (facility: Facility) => void;
}

export const DetailsPanel = ({ facility, isNew, onSave }: DetailsPanelProps) => {
  const [formData, setFormData] = useState<Facility | null>(facility);

  useEffect(() => {
    setFormData(facility);
  }, [facility]);

  if (!formData) {
    return <div className="details-panel">No facility selected</div>;
  }

  const handleChange = (field: keyof Facility, value: string) => {
    setFormData(prev => prev ? { ...prev, [field]: value } : null);
  };

  const handleSave = () => {
    if (formData) {
      onSave(formData);
    }
  };

  return (
    <div className="details-panel">
      <h2 className="panel-title">
        {isNew ? 'Add New Facility' : 'Facility Details'}
      </h2>
      <div className="details-form">
        <FormRow 
          label="Facility Name"
          id="name"
          value={formData.name}
          onChange={e => handleChange('name', e.target.value)}
        />
        <FormRow 
          label="Type"
          id="type"
          type="select"
          value={formData.type}
          options={facilityTypes}
          onChange={e => handleChange('type', e.target.value)}
        />
        <FormRow 
          label="Amount"
          id="amount"
          value={formData.amount}
          onChange={e => handleChange('amount', e.target.value)}
        />
        <FormRow 
          label="Rate"
          id="rate"
          value={formData.rate}
          onChange={e => handleChange('rate', e.target.value)}
        />
        <FormRow 
          label="Maturity Date"
          id="maturityDate"
          type="date"
          value={formData.maturityDate}
          onChange={e => handleChange('maturityDate', e.target.value)}
        />
        <FormActions 
          onCancel={() => setFormData(facility)}
          onSave={handleSave}
        />
      </div>
    </div>
  );
};

interface FormRowProps {
  label: string;
  id: string;
  type?: 'text' | 'date' | 'select';
  value?: string;
  options?: string[];
  onChange?: (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;
}

const FormRow = ({ label, id, type = 'text', value = '', options = [], onChange }: FormRowProps) => (
  <div className="form-row">
    <label htmlFor={id}>{label}</label>
    {type === 'select' ? (
      <select 
        id={id} 
        value={value} 
        onChange={onChange}
      >
        {options.map(option => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    ) : (
      <input 
        type={type} 
        id={id} 
        value={value} 
        onChange={onChange}
      />
    )}
  </div>
);

const FormActions = ({ 
  onCancel, 
  onSave 
}: { 
  onCancel: () => void; 
  onSave: () => void;
}) => (
  <div className="form-actions">
    <button className="btn-secondary" onClick={onCancel}>Cancel</button>
    <button className="btn-primary" onClick={onSave}>Save Changes</button>
  </div>
); 