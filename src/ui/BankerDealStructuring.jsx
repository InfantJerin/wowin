import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Plus, Users, Save, RefreshCw, ChevronDown, BarChart, DollarSign } from 'lucide-react';

// Custom Table Components
const TableHeader = ({ children }) => <div className="border-b border-gray-200">{children}</div>;
const TableRow = ({ children, className = "" }) => <div className={`flex items-center border-b border-gray-200 last:border-b-0 ${className}`}>{children}</div>;
const TableCell = ({ children, className = "" }) => <div className={`p-4 flex-1 ${className}`}>{children}</div>;
const TableHeadCell = ({ children, className = "" }) => <div className={`p-4 flex-1 font-medium text-gray-500 text-sm ${className}`}>{children}</div>;

const BankerDealStructuringApp = () => {
  const [activeUsers, setActiveUsers] = useState([
    { id: 1, name: 'John Carter', role: 'Lead Banker', status: 'Editing' },
    { id: 2, name: 'Sarah Mitchell', role: 'Credit Analyst', status: 'Viewing' }
  ]);
  
  const [structures, setStructures] = useState([
    { id: 'struct-1', name: 'Base Case', roae: '12.4%', lastModified: '2 mins ago', scenarios: 3 },
    { id: 'struct-2', name: 'Upside Case', roae: '15.7%', lastModified: '25 mins ago', scenarios: 2 }
  ]);
  
  return (
    <div className="bg-gray-50 min-h-screen p-4">
      <div className="max-w-6xl mx-auto">
        <header className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Deal Structuring Workspace</h1>
            <p className="text-gray-500">Project: Acquisition Financing - ABC Corp</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" className="flex items-center gap-2">
              <Users size={16} />
              <span>Active Users ({activeUsers.length})</span>
            </Button>
            <Button variant="outline" className="flex items-center gap-2">
              <Save size={16} />
              <span>Save</span>
            </Button>
          </div>
        </header>
        
        <div className="grid grid-cols-4 gap-6 mb-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Deal Size</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">$750M</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">GS Commitment</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">$150M</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Best ROAE</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-green-600">15.7%</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Structures</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{structures.length}</p>
            </CardContent>
          </Card>
        </div>
        
        <Tabs defaultValue="structures" className="mb-6">
          <TabsList className="mb-4">
            <TabsTrigger value="structures">Structures</TabsTrigger>
            <TabsTrigger value="tranches">Tranches</TabsTrigger>
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
          </TabsList>
          
          <TabsContent value="structures" className="mt-0">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Deal Structures</CardTitle>
                  <Button className="flex items-center gap-2">
                    <Plus size={16} />
                    <span>New Structure</span>
                  </Button>
                </div>
                <CardDescription>
                  Create and compare multiple structures to optimize ROAE
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="rounded-md border border-gray-200 overflow-hidden">
                  <TableHeader>
                    <TableRow className="bg-gray-50">
                      <TableHeadCell>Structure Name</TableHeadCell>
                      <TableHeadCell>Scenarios</TableHeadCell>
                      <TableHeadCell>ROAE</TableHeadCell>
                      <TableHeadCell>Last Modified</TableHeadCell>
                      <TableHeadCell>Actions</TableHeadCell>
                    </TableRow>
                  </TableHeader>
                  <div>
                    {structures.map(structure => (
                      <TableRow key={structure.id}>
                        <TableCell className="font-medium">{structure.name}</TableCell>
                        <TableCell>{structure.scenarios}</TableCell>
                        <TableCell className="font-bold">{structure.roae}</TableCell>
                        <TableCell>{structure.lastModified}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Button variant="outline" size="sm">Edit</Button>
                            <Button variant="outline" size="sm">Clone</Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="tranches" className="mt-0">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Loan Tranches</CardTitle>
                  <div className="flex gap-2">
                    <Select defaultValue="struct-1">
                      <SelectTrigger className="w-48">
                        <SelectValue placeholder="Select structure" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="struct-1">Base Case</SelectItem>
                        <SelectItem value="struct-2">Upside Case</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button className="flex items-center gap-2">
                      <Plus size={16} />
                      <span>Add Tranche</span>
                    </Button>
                  </div>
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
                      <TableHeadCell>Actions</TableHeadCell>
                    </TableRow>
                  </TableHeader>
                  <div>
                    <TableRow>
                      <TableCell className="font-medium">Term Loan A</TableCell>
                      <TableCell>Term</TableCell>
                      <TableCell>USD</TableCell>
                      <TableCell>$400M</TableCell>
                      <TableCell>$80M</TableCell>
                      <TableCell>LIBOR + 350bps</TableCell>
                      <TableCell>
                        <Button variant="outline" size="sm">Edit</Button>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-medium">Revolving Credit</TableCell>
                      <TableCell>RCF</TableCell>
                      <TableCell>USD</TableCell>
                      <TableCell>$350M</TableCell>
                      <TableCell>$70M</TableCell>
                      <TableCell>LIBOR + 325bps</TableCell>
                      <TableCell>
                        <Button variant="outline" size="sm">Edit</Button>
                      </TableCell>
                    </TableRow>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="analysis" className="mt-0">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>ROAE Analysis</CardTitle>
                  <div className="flex gap-2">
                    <Button variant="outline" className="flex items-center gap-2">
                      <RefreshCw size={16} />
                      <span>Recalculate</span>
                    </Button>
                    <Button variant="outline" className="flex items-center gap-2">
                      <BarChart size={16} />
                      <span>Compare Structures</span>
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-6">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-lg">Base Case Structure</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">ROAE:</span>
                          <span className="font-bold">12.4%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Total Revenue:</span>
                          <span className="font-bold">$24.5M</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Capital Usage:</span>
                          <span className="font-bold">$75.2M</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Fees:</span>
                          <span className="font-bold">$7.8M</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-lg">Upside Case Structure</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">ROAE:</span>
                          <span className="font-bold text-green-600">15.7%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Total Revenue:</span>
                          <span className="font-bold">$32.1M</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Capital Usage:</span>
                          <span className="font-bold">$78.5M</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Fees:</span>
                          <span className="font-bold">$10.2M</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
        
        <div className="flex gap-6">
          <Card className="w-1/3">
            <CardHeader>
              <CardTitle>Active Collaborators</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {activeUsers.map(user => (
                  <div key={user.id} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-medium">
                        {user.name.charAt(0)}
                      </div>
                      <div>
                        <p className="font-medium">{user.name}</p>
                        <p className="text-sm text-gray-500">{user.role}</p>
                      </div>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      user.status === 'Editing' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {user.status}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
            <CardFooter>
              <Button variant="outline" className="w-full">Invite Collaborator</Button>
            </CardFooter>
          </Card>
          
          <Card className="w-2/3">
            <CardHeader>
              <CardTitle>Activity Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-medium">
                    J
                  </div>
                  <div>
                    <p><span className="font-medium">John Carter</span> updated interest rate for Term Loan A to LIBOR + 350bps</p>
                    <p className="text-sm text-gray-500">2 minutes ago</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-medium">
                    S
                  </div>
                  <div>
                    <p><span className="font-medium">Sarah Mitchell</span> created a new structure "Upside Case"</p>
                    <p className="text-sm text-gray-500">25 minutes ago</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-medium">
                    J
                  </div>
                  <div>
                    <p><span className="font-medium">John Carter</span> modified GS commitment size to $150M</p>
                    <p className="text-sm text-gray-500">1 hour ago</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default BankerDealStructuringApp;