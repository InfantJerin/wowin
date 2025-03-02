import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ChevronDown, ChevronRight, X, Save, Edit, Plus, Search } from 'lucide-react';

// Custom Table Components
const TableHeader = ({ children }) => <div className="border-b border-gray-200">{children}</div>;
const TableRow = ({ children, className = "", onClick }) => <div className={`flex items-center border-b border-gray-200 last:border-b-0 hover:bg-gray-50 cursor-pointer ${className}`} onClick={onClick}>{children}</div>;
const TableCell = ({ children, className = "" }) => <div className={`p-4 flex-1 ${className}`}>{children}</div>;
const TableHeadCell = ({ children, className = "" }) => <div className={`p-4 flex-1 font-medium text-gray-500 text-sm ${className}`}>{children}</div>;

// Accordion Component for Field Groups
const Accordion = ({ title, children, defaultOpen = false }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  
  return (
    <div className="border border-gray-200 rounded-md mb-4">
      <div 
        className="flex items-center justify-between p-4 bg-gray-50 cursor-pointer" 
        onClick={() => setIsOpen(!isOpen)}
      >
        <h3 className="font-medium text-gray-800">{title}</h3>
        {isOpen ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
      </div>
      {isOpen && (
        <div className="p-4 border-t border-gray-200">
          {children}
        </div>
      )}
    </div>
  );
};

// Form Field Component
const FormField = ({ label, children, required = false }) => (
  <div className="mb-4">
    <label className="block text-sm font-medium text-gray-700 mb-1">
      {label} {required && <span className="text-red-500">*</span>}
    </label>
    {children}
  </div>
);

const BankerDealStructuringApp = () => {
  const [showDrawer, setShowDrawer] = useState(false);
  const [selectedTrancheId, setSelectedTrancheId] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  
  const tranches = [
    { 
      id: 'tranche-1', 
      name: 'Term Loan A', 
      type: 'Term',
      currency: 'USD',
      totalSize: '$400M',
      gsSize: '$80M',
      interestRate: 'LIBOR + 350bps'
    },
    { 
      id: 'tranche-2', 
      name: 'Revolving Credit', 
      type: 'RCF',
      currency: 'USD',
      totalSize: '$350M',
      gsSize: '$70M',
      interestRate: 'LIBOR + 325bps'
    }
  ];
  
  const handleEditTranche = (trancheId) => {
    setSelectedTrancheId(trancheId);
    setShowDrawer(true);
  };
  
  const closeDrawer = () => {
    setShowDrawer(false);
    setSelectedTrancheId(null);
  };
  
  // Filter fields based on search term
  const filterFields = (fieldLabel) => {
    if (!searchTerm) return true;
    return fieldLabel.toLowerCase().includes(searchTerm.toLowerCase());
  };
  
  return (
    <div className="bg-gray-50 min-h-screen">
      <div className="max-w-6xl mx-auto p-4">
        <header className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Deal Structuring Workspace</h1>
            <p className="text-gray-500">Project: Acquisition Financing - ABC Corp</p>
          </div>
        </header>
        
        <Card className="mb-6">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Loan Tranches</CardTitle>
              <Button className="flex items-center gap-2" onClick={() => handleEditTranche('new')}>
                <Plus size={16} />
                <span>Add Tranche</span>
              </Button>
            </div>
            <CardDescription>
              Manage tranches for the selected structure
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border border-gray-200 overflow-hidden">
              <TableHeader>
                <TableRow className="bg-gray-50">
                  <TableHeadCell>Tranche Name</TableHeadCell>
                  <TableHeadCell>Type</TableHeadCell>
                  <TableHeadCell>Currency</TableHeadCell>
                  <TableHeadCell>Total Size</TableHeadCell>
                  <TableHeadCell>GS Size</TableHeadCell>
                  <TableHeadCell>Interest Rate</TableHeadCell>
                  <TableHeadCell className="w-24">Actions</TableHeadCell>
                </TableRow>
              </TableHeader>
              <div>
                {tranches.map((tranche) => (
                  <TableRow 
                    key={tranche.id}
                    onClick={() => handleEditTranche(tranche.id)}
                  >
                    <TableCell className="font-medium">{tranche.name}</TableCell>
                    <TableCell>{tranche.type}</TableCell>
                    <TableCell>{tranche.currency}</TableCell>
                    <TableCell>{tranche.totalSize}</TableCell>
                    <TableCell>{tranche.gsSize}</TableCell>
                    <TableCell>{tranche.interestRate}</TableCell>
                    <TableCell className="w-24">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEditTranche(tranche.id);
                        }}
                      >
                        <Edit size={14} className="mr-1" /> Edit
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Slide-out Drawer for Tranche Editing */}
      {showDrawer && (
        <div className="fixed inset-0 bg-black bg-opacity-20 z-10 flex justify-end">
          <div className="bg-white w-2/3 max-w-2xl overflow-auto shadow-xl animate-slide-in-right">
            <div className="sticky top-0 bg-white z-10 border-b border-gray-200">
              <div className="flex justify-between items-center p-4">
                <h2 className="text-xl font-bold">
                  {selectedTrancheId === 'new' ? 'Add New Tranche' : 'Edit Tranche'}
                </h2>
                <Button variant="ghost" size="sm" onClick={closeDrawer}>
                  <X size={18} />
                </Button>
              </div>
              
              {/* Search Field */}
              <div className="px-4 pb-4">
                <div className="relative">
                  <Search size={16} className="absolute left-3 top-2.5 text-gray-400" />
                  <Input 
                    placeholder="Search fields..."
                    className="pl-9"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)} 
                  />
                </div>
              </div>
            </div>
            
            <div className="p-4">
              <Accordion title="Basic Information" defaultOpen={true}>
                <div className="grid grid-cols-2 gap-4">
                  {filterFields('Tranche Name') && (
                    <FormField label="Tranche Name" required>
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? 'Term Loan A' : ''} placeholder="Enter tranche name" />
                    </FormField>
                  )}
                  
                  {filterFields('Tranche Type') && (
                    <FormField label="Tranche Type" required>
                      <Select defaultValue={selectedTrancheId === 'tranche-1' ? 'term' : ''}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="term">Term</SelectItem>
                          <SelectItem value="rcf">RCF</SelectItem>
                          <SelectItem value="bridge">Bridge</SelectItem>
                        </SelectContent>
                      </Select>
                    </FormField>
                  )}
                  
                  {filterFields('Transaction ID') && (
                    <FormField label="Transaction ID">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? 'TX-20250302-001' : ''} placeholder="Transaction ID" />
                    </FormField>
                  )}
                  
                  {filterFields('SL Deal Number') && (
                    <FormField label="SL Deal Number">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? 'SL-10392' : ''} placeholder="SL Deal Number" />
                    </FormField>
                  )}
                  
                  {filterFields('Tranche ID') && (
                    <FormField label="Tranche ID">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? 'TID-8822' : ''} readOnly className="bg-gray-50" />
                    </FormField>
                  )}
                  
                  {filterFields('Transaction State') && (
                    <FormField label="Transaction State">
                      <Select defaultValue={selectedTrancheId === 'tranche-1' ? 'active' : ''}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select state" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="active">Active</SelectItem>
                          <SelectItem value="pending">Pending</SelectItem>
                          <SelectItem value="closed">Closed</SelectItem>
                        </SelectContent>
                      </Select>
                    </FormField>
                  )}
                  
                  {filterFields('Project Name') && (
                    <FormField label="Project Name">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? 'Project Phoenix' : ''} placeholder="Project name" />
                    </FormField>
                  )}
                  
                  {filterFields('Native Currency') && (
                    <FormField label="Native Currency" required>
                      <Select defaultValue={selectedTrancheId === 'tranche-1' ? 'usd' : ''}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select currency" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="usd">USD</SelectItem>
                          <SelectItem value="eur">EUR</SelectItem>
                          <SelectItem value="gbp">GBP</SelectItem>
                        </SelectContent>
                      </Select>
                    </FormField>
                  )}
                </div>
              </Accordion>
              
              <Accordion title="Sizing and Commitments">
                <div className="grid grid-cols-2 gap-4">
                  {filterFields('Total Size') && (
                    <FormField label="Total Size" required>
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? '400000000' : ''} placeholder="Enter total size" />
                    </FormField>
                  )}
                  
                  {filterFields('GS Size') && (
                    <FormField label="GS Size" required>
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? '80000000' : ''} placeholder="Enter GS size" />
                    </FormField>
                  )}
                  
                  {filterFields('GS Commitment Native') && (
                    <FormField label="GS Commitment Native">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? '80000000' : ''} placeholder="GS commitment" />
                    </FormField>
                  )}
                  
                  {filterFields('Approved Credit Hold Native') && (
                    <FormField label="Approved Credit Hold Native">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? '40000000' : ''} placeholder="Credit hold" />
                    </FormField>
                  )}
                  
                  {filterFields('Committee Approved Commitment Native') && (
                    <FormField label="Committee Approved Commitment Native">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? '80000000' : ''} placeholder="Committee approved" />
                    </FormField>
                  )}
                  
                  {filterFields('Approved Relationship Hold Native') && (
                    <FormField label="Approved Relationship Hold Native">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? '35000000' : ''} placeholder="Relationship hold" />
                    </FormField>
                  )}
                  
                  {filterFields('GS Bank Approved Commitment Native') && (
                    <FormField label="GS Bank Approved Commitment Native">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? '50000000' : ''} placeholder="GS Bank commitment" />
                    </FormField>
                  )}
                  
                  {filterFields('GSIB Approved Commitment Native') && (
                    <FormField label="GSIB Approved Commitment Native">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? '30000000' : ''} placeholder="GSIB commitment" />
                    </FormField>
                  )}
                  
                  {filterFields('GSIB Approved Hold Native') && (
                    <FormField label="GSIB Approved Hold Native">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? '20000000' : ''} placeholder="GSIB hold" />
                    </FormField>
                  )}
                  
                  {filterFields('GS Bank Approved Hold Native') && (
                    <FormField label="GS Bank Approved Hold Native">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? '25000000' : ''} placeholder="GS Bank hold" />
                    </FormField>
                  )}
                </div>
              </Accordion>
              
              <Accordion title="Pricing and Terms">
                <div className="grid grid-cols-2 gap-4">
                  {filterFields('Interest Rate Margin BPS') && (
                    <FormField label="Interest Rate Margin BPS" required>
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? '350' : ''} placeholder="Margin in basis points" />
                    </FormField>
                  )}
                  
                  {filterFields('Price Flex BPS') && (
                    <FormField label="Price Flex BPS">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? '50' : ''} placeholder="Price flex in basis points" />
                    </FormField>
                  )}
                  
                  {filterFields('OID') && (
                    <FormField label="OID">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? '0.5' : ''} placeholder="Original issue discount" />
                    </FormField>
                  )}
                  
                  {filterFields('Term Loan Flex') && (
                    <FormField label="Term Loan Flex">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? '0.25' : ''} placeholder="Term loan flex" />
                    </FormField>
                  )}
                  
                  {filterFields('GS Role') && (
                    <FormField label="GS Role">
                      <Select defaultValue={selectedTrancheId === 'tranche-1' ? 'lead' : ''}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select role" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="lead">Lead Arranger</SelectItem>
                          <SelectItem value="bookrunner">Bookrunner</SelectItem>
                          <SelectItem value="participant">Participant</SelectItem>
                        </SelectContent>
                      </Select>
                    </FormField>
                  )}
                  
                  {filterFields('Accounting Treatment') && (
                    <FormField label="Accounting Treatment">
                      <Select defaultValue={selectedTrancheId === 'tranche-1' ? 'fvoci' : ''}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select treatment" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="fvoci">FVOCI</SelectItem>
                          <SelectItem value="fvtpl">FVTPL</SelectItem>
                          <SelectItem value="amortized">Amortized Cost</SelectItem>
                        </SelectContent>
                      </Select>
                    </FormField>
                  )}
                  
                  {filterFields('Maturity Tenor') && (
                    <FormField label="Maturity Tenor">
                      <div className="flex gap-2">
                        <Input defaultValue={selectedTrancheId === 'tranche-1' ? '5' : ''} placeholder="Tenor" />
                        <Select defaultValue={selectedTrancheId === 'tranche-1' ? 'years' : ''} className="w-1/2">
                          <SelectTrigger>
                            <SelectValue placeholder="Period" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="days">Days</SelectItem>
                            <SelectItem value="months">Months</SelectItem>
                            <SelectItem value="years">Years</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </FormField>
                  )}
                  
                  {filterFields('Seniority') && (
                    <FormField label="Seniority">
                      <Select defaultValue={selectedTrancheId === 'tranche-1' ? 'senior' : ''}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select seniority" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="senior">Senior</SelectItem>
                          <SelectItem value="subordinated">Subordinated</SelectItem>
                          <SelectItem value="junior">Junior</SelectItem>
                        </SelectContent>
                      </Select>
                    </FormField>
                  )}
                </div>
              </Accordion>
              
              <Accordion title="Dates and Timeline">
                <div className="grid grid-cols-2 gap-4">
                  {filterFields('FTT Date') && (
                    <FormField label="FTT Date">
                      <Input type="date" defaultValue={selectedTrancheId === 'tranche-1' ? '2025-01-15' : ''} />
                    </FormField>
                  )}
                  
                  {filterFields('Priced Date') && (
                    <FormField label="Priced Date">
                      <Input type="date" defaultValue={selectedTrancheId === 'tranche-1' ? '2025-01-20' : ''} />
                    </FormField>
                  )}
                  
                  {filterFields('Announced Date') && (
                    <FormField label="Announced Date">
                      <Input type="date" defaultValue={selectedTrancheId === 'tranche-1' ? '2025-01-10' : ''} />
                    </FormField>
                  )}
                  
                  {filterFields('Expected Closing Date') && (
                    <FormField label="Expected Closing Date">
                      <Input type="date" defaultValue={selectedTrancheId === 'tranche-1' ? '2025-04-15' : ''} />
                    </FormField>
                  )}
                  
                  {filterFields('Commitment Date') && (
                    <FormField label="Commitment Date">
                      <Input type="date" defaultValue={selectedTrancheId === 'tranche-1' ? '2025-01-25' : ''} />
                    </FormField>
                  )}
                  
                  {filterFields('Double Signing Date') && (
                    <FormField label="Double Signing Date">
                      <Input type="date" defaultValue={selectedTrancheId === 'tranche-1' ? '' : ''} />
                    </FormField>
                  )}
                  
                  {filterFields('Commitment Length') && (
                    <FormField label="Commitment Length">
                      <div className="flex gap-2">
                        <Input defaultValue={selectedTrancheId === 'tranche-1' ? '3' : ''} placeholder="Length" />
                        <Select defaultValue={selectedTrancheId === 'tranche-1' ? 'months' : ''} className="w-1/2">
                          <SelectTrigger>
                            <SelectValue placeholder="Period" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="days">Days</SelectItem>
                            <SelectItem value="months">Months</SelectItem>
                            <SelectItem value="years">Years</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </FormField>
                  )}
                </div>
              </Accordion>
              
              <Accordion title="Credit Details">
                <div className="grid grid-cols-2 gap-4">
                  {filterFields('Credit Agreement Name') && (
                    <FormField label="Credit Agreement Name">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? 'ABC Corp Credit Agreement' : ''} placeholder="Credit agreement name" />
                    </FormField>
                  )}
                  
                  {filterFields('Original Purpose') && (
                    <FormField label="Original Purpose">
                      <Select defaultValue={selectedTrancheId === 'tranche-1' ? 'acquisition' : ''}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select purpose" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="acquisition">Acquisition</SelectItem>
                          <SelectItem value="refinancing">Refinancing</SelectItem>
                          <SelectItem value="working-capital">Working Capital</SelectItem>
                          <SelectItem value="capex">Capital Expenditure</SelectItem>
                        </SelectContent>
                      </Select>
                    </FormField>
                  )}
                  
                  {filterFields('Credit Rating ICR') && (
                    <FormField label="Credit Rating ICR">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? 'BB+' : ''} placeholder="Credit rating" />
                    </FormField>
                  )}
                  
                  {filterFields('Credit Rating ICR Numeric') && (
                    <FormField label="Credit Rating ICR Numeric">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? '11' : ''} placeholder="Numeric rating" />
                    </FormField>
                  )}
                  
                  {filterFields('Issuer ID') && (
                    <FormField label="Issuer ID">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? '4522' : ''} placeholder="Issuer ID" />
                    </FormField>
                  )}
                  
                  {filterFields('Material Changes For Leveraged Loan') && (
                    <FormField label="Material Changes For Leveraged Loan">
                      <Select defaultValue={selectedTrancheId === 'tranche-1' ? 'no' : ''}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="yes">Yes</SelectItem>
                          <SelectItem value="no">No</SelectItem>
                        </SelectContent>
                      </Select>
                    </FormField>
                  )}
                  
                  {filterFields('Negative Changes To Material Conditions Precedents') && (
                    <FormField label="Negative Changes To Material Conditions Precedents">
                      <Select defaultValue={selectedTrancheId === 'tranche-1' ? 'no' : ''}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="yes">Yes</SelectItem>
                          <SelectItem value="no">No</SelectItem>
                        </SelectContent>
                      </Select>
                    </FormField>
                  )}
                </div>
              </Accordion>
              
              <Accordion title="Additional Information">
                <div className="grid grid-cols-2 gap-4">
                  {filterFields('Strategy') && (
                    <FormField label="Strategy">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? 'Hold and distribute' : ''} placeholder="Strategy" />
                    </FormField>
                  )}
                  
                  {filterFields('Investment Source') && (
                    <FormField label="Investment Source">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? 'Internal' : ''} placeholder="Investment source" />
                    </FormField>
                  )}
                  
                  {filterFields('Anticipated Fronting') && (
                    <FormField label="Anticipated Fronting">
                      <Select defaultValue={selectedTrancheId === 'tranche-1' ? 'yes' : ''}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="yes">Yes</SelectItem>
                          <SelectItem value="no">No</SelectItem>
                        </SelectContent>
                      </Select>
                    </FormField>
                  )}
                  
                  {filterFields('Lending Designation') && (
                    <FormField label="Lending Designation">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? 'Core' : ''} placeholder="Lending designation" />
                    </FormField>
                  )}
                  
                  {filterFields('Commitment Type Code') && (
                    <FormField label="Commitment Type Code">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? 'FIRM' : ''} placeholder="Commitment type code" />
                    </FormField>
                  )}
                  
                  {filterFields('Refinanced Tranches') && (
                    <FormField label="Refinanced Tranches">
                      <Input defaultValue={selectedTrancheId === 'tranche-1' ? '' : ''} placeholder="Refinanced tranches" />
                    </FormField>
                  )}
                </div>
              </Accordion>
            </div>
            
            <div className="sticky bottom-0 bg-white border-t border-gray-200 p-4 flex justify-end gap-2">
              <Button variant="outline" onClick={closeDrawer}>Cancel</Button>
              <Button className="flex items-center gap-2">
                <Save size={16} />
                <span>Save Tranche</span>
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BankerDealStructuringApp;