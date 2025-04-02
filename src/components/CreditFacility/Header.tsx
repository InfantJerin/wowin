import React from 'react';
import { FormGroup } from './FormGroup';

interface HeaderProps {
  borrower?: string;
  agreementDate?: string;
  onBorrowerChange?: (value: string) => void;
  onDateChange?: (value: string) => void;
}

export const Header = ({ 
  borrower = '', 
  agreementDate = '',
  onBorrowerChange,
  onDateChange
}: HeaderProps) => {
  return (
    <div className="header">
      <div className="header-form">
        <FormGroup
          label="Borrower"
          id="borrower"
          type="text"
          placeholder="Enter borrower name"
          value={borrower}
          onChange={(e) => onBorrowerChange?.(e.target.value)}
        />
        <FormGroup
          label="Agreement Date"
          id="agreement-date"
          type="date"
          value={agreementDate}
          onChange={(e) => onDateChange?.(e.target.value)}
        />
      </div>
    </div>
  );
}; 