import React from 'react';
import type { Facility } from '../../types/facility';

interface FacilitiesPanelProps {
  facilities: Facility[];
  onSelect: (facility: Facility) => void;
  activeFacilityId?: string;
  onAddNew: () => void;
}

export const FacilitiesPanel = ({ 
  facilities, 
  onSelect, 
  activeFacilityId,
  onAddNew 
}: FacilitiesPanelProps) => {
  return (
    <div className="facilities-panel">
      <h2 className="panel-title">Facility</h2>
      <div className="facility-list">
        {facilities.map(facility => (
          <FacilityItem 
            key={facility.id} 
            {...facility} 
            isActive={facility.id === activeFacilityId}
            onClick={() => onSelect(facility)}
          />
        ))}
      </div>
      <AddFacilityButton onClick={onAddNew} />
    </div>
  );
};

interface FacilityItemProps {
  id: string;
  name: string;
  type: string;
  amount: string;
  rate: string;
  maturityDate: string;
  isActive?: boolean;
  onClick: () => void;
}

const FacilityItem = ({ name, type, amount, isActive, onClick }: FacilityItemProps) => (
  <div className={`facility-item ${isActive ? 'active' : ''}`} onClick={onClick}>
    <div className="facility-name">{name}</div>
    <div className="facility-meta">
      <MetaItem label="Type" value={type} />
      <MetaItem label="Amount" value={amount} />
    </div>
  </div>
);

const MetaItem = ({ label, value }: { label: string; value: string }) => (
  <div>
    <div className="meta-label">{label}</div>
    <div className="meta-value">{value}</div>
  </div>
);

const AddFacilityButton = ({ onClick }: { onClick: () => void }) => (
  <div className="add-facility" onClick={onClick}>
    <span className="add-icon">+</span> Add Facility
  </div>
); 