import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { FacilitiesPanel } from '../FacilitiesPanel';

// Mock data
const mockFacilities = Array.from({ length: 20 }, (_, i) => ({
  id: `facility-${i}`,
  name: `Facility ${String.fromCharCode(65 + i)}`,
  type: 'Term Loan',
  amount: `$${(i + 1) * 1000000}`,
  rate: '4.25%',
  maturityDate: '2030-05-15'
}));

describe('FacilitiesPanel', () => {
  const mockProps = {
    facilities: mockFacilities,
    onSelect: jest.fn(),
    onAddNew: jest.fn(),
    activeFacilityId: 'facility-0'
  };

  beforeEach(() => {
    // Set up a fixed container size to test scrolling
    const container = document.createElement('div');
    container.style.height = '600px';
    container.style.width = '400px';
    document.body.appendChild(container);
  });

  it('renders all facilities and add button', () => {
    render(<FacilitiesPanel {...mockProps} />);
    
    // Check if all facilities are rendered
    mockFacilities.forEach(facility => {
      expect(screen.getByText(facility.name)).toBeInTheDocument();
    });

    // Check if add button is visible
    expect(screen.getByText(/add facility/i)).toBeInTheDocument();
  });

  it('maintains add button visibility when scrolling', () => {
    const { container } = render(<FacilitiesPanel {...mockProps} />);
    
    const facilityList = container.querySelector('.facility-list');
    const addButton = screen.getByText(/add facility/i);

    // Scroll to bottom
    if (facilityList) {
      facilityList.scrollTop = facilityList.scrollHeight;
    }

    // Add button should still be visible
    expect(addButton).toBeVisible();
    
    // Check if add button is outside the scrollable area
    expect(addButton.closest('.facility-list')).toBeNull();
  });

  it('handles facility selection', async () => {
    render(<FacilitiesPanel {...mockProps} />);
    
    const facilityItem = screen.getByText('Facility B');
    await userEvent.click(facilityItem);
    
    expect(mockProps.onSelect).toHaveBeenCalled();
  });

  it('handles add new facility', async () => {
    render(<FacilitiesPanel {...mockProps} />);
    
    const addButton = screen.getByText(/add facility/i);
    await userEvent.click(addButton);
    
    expect(mockProps.onAddNew).toHaveBeenCalled();
  });

  it('maintains correct layout structure', () => {
    const { container } = render(<FacilitiesPanel {...mockProps} />);
    
    const panel = container.querySelector('.facilities-panel');
    const list = container.querySelector('.facility-list');
    const addButton = container.querySelector('.add-facility');

    // Check if elements are direct children of panel in correct order
    expect(panel?.children[0]).toHaveClass('panel-title');
    expect(panel?.children[1]).toHaveClass('facility-list');
    expect(panel?.children[2]).toHaveClass('add-facility');

    // Check if list is scrollable
    expect(list).toHaveStyle({ overflowY: 'auto' });
    
    // Check if add button is outside scroll area
    expect(addButton?.parentElement).toBe(panel);
  });
}); 