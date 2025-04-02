describe('Facilities Panel', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5173') // Your Vite dev server URL
  })

  it('should display facilities list and add button', () => {
    // Check if facilities are visible
    cy.get('.facility-item').should('have.length.greaterThan', 0)
    
    // Verify add button is visible
    cy.get('.add-facility').should('be.visible')
  })



  it('should open add facility form', () => {
    // Click add facility button
    cy.get('.add-facility').click()
    
    // Verify form is visible
    cy.get('.details-panel').should('be.visible')
  })

  it('should add multiple facilities and maintain add button visibility', () => {
    // Add 5 facilities
    for (let i = 0; i < 5; i++) {
      cy.get('.add-facility').click()
      
      // Wait for form to be visible and fill details
      cy.get('.details-panel').should('be.visible')
      cy.get('#name').should('be.visible').type(`New Facility ${i + 1}`)
      cy.get('#type').should('be.visible').select('Term Loan')
      cy.get('#amount').should('be.visible').type('1000000')
      cy.get('#rate').should('be.visible').type('4.25')
      cy.get('#maturityDate').should('be.visible').type('2025-12-31')
      
      // Save the facility
      cy.get('.btn-primary').click()
      

    }

    // Verify all facilities are added
    cy.get('.facility-item').should('have.length', 6)
    
    // Scroll to bottom
    cy.get('.facility-list').scrollTo('bottom')
    
    // Verify add button is still visible
    cy.get('.add-facility').should('be.visible')
  })
}) 