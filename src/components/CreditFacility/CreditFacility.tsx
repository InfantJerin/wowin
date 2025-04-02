import React, { useState } from 'react';
import { Header } from './Header';
import { FacilitiesPanel } from './FacilitiesPanel';
import { DetailsPanel } from './DetailsPanel';
import './CreditFacility.css';
import { facilities as initialFacilities } from '../../data/facilityData';
import type { Facility } from '../../types/facility';

export const CreditFacility = () => {
  const [facilityList, setFacilityList] = useState<Facility[]>(initialFacilities);
  const [activeFacility, setActiveFacility] = useState<Facility | null>(facilityList[0]);
  const [isAddingNew, setIsAddingNew] = useState(false);

  const handleAddNewFacility = () => {
    const newFacility: Facility = {
      id: `facility-${Date.now()}`,
      name: '',
      type: 'Term Loan',
      amount: '',
      rate: '',
      maturityDate: '',
      isActive: true
    };
    setIsAddingNew(true);
    setActiveFacility(newFacility);
  };

  const handleSaveFacility = (facility: Facility) => {
    if (isAddingNew) {
      setFacilityList(prev => [...prev, facility]);
      setIsAddingNew(false);
    } else {
      setFacilityList(prev => 
        prev.map(f => f.id === facility.id ? facility : f)
      );
    }
    setActiveFacility(facility);
  };

  return (
    <div className="container">
      <Header />
      <div className="main-content">
        <FacilitiesPanel 
          facilities={facilityList}
          onSelect={setActiveFacility}
          activeFacilityId={activeFacility?.id}
          onAddNew={handleAddNewFacility}
        />
        <DetailsPanel 
          facility={activeFacility}
          isNew={isAddingNew}
          onSave={handleSaveFacility}
        />
      </div>
    </div>
  );
}; 