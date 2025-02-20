from pydantic import BaseModel
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Document(BaseModel):
    transactionId: str
    transactionState: str
    documentId: str
    fileName: str
    url: str
    documentType: str
    modifiedDate: str

class CommitteeInfo(BaseModel):
    transactionId: str
    transactionState: str
    committee: str
    committeeDate: str
    reviewedByCuoGuid: str
    delegatedProcessCode: str
    approvedBy: str
    committeeApprovalStatus: str
    committeeApprovalComment: str
    gsbankApprovalComment: str
    gsbankApprovalStatus: str
    gsibApprovalComment: str
    gsibApprovalStatus: str

class CreditAgreement(BaseModel):
    transactionId: str
    creditAgreementId: int
    obligorId: int
    obligorEntity: str
    agentBankId: int
    agentBankEntity: str
    guarantorId: int
    guarantorEntity: str
    lendingDesignation: str
    typeOfLoan: str
    isBilateralDeal: bool
    primarySourceOfRepaymentEntity: str
    isGSAgentBank: str
    materialChangesForLeveragedLoan: str

class CreditAssessment(BaseModel):
    transactionId: str
    scenarioId: str
    obligorId: int
    financingLeverage: float
    reportedEBITDA: float
    financingEBITDA: float
    fundedDebt: float
    unfundedDebt: float
    revenueProformaltm: float
    proformaCashBalanceOfCompany: float
    enterpriseValueOfCompany: float
    estimatedTotalAssetsOfCompany: float
    cumulativeFreecashFlow: float
    discountedCashFlowInfo: float
    finacicalAsOfDateForBorrower: str
    creditAssesmentSubmittedBy: str
    isUnderwriting: bool
    IsLeveragedLending: bool
    currency: str

class GSBookingEntity(BaseModel):
    transactionId: str
    transactionState: str
    trancheID: int
    gsBookingEntityEmmaId: int

class LoanMaturity(BaseModel):
    maturityPeriod: int
    maturityUnit: str

class Rating(BaseModel):
    moody: str
    sp: str

class Instrument(BaseModel):
    trancheId: str
    currency: str
    primeId: str
    dealPrimeId: str
    interestRateBps: float
    loanMaturity: LoanMaturity
    rating: Rating
    oid: float

class Investor(BaseModel):
    investorId: str
    investorName: str
    investorType: str
    investorNationality: str
    investorContactId: str
    investorContactName: str

class KeyDates(BaseModel):
    transactionId: str
    transactionState: str
    commitmentExpirationDate: date
    commitmentLetterDate: date
    committeeApprovalDate: date
    commitmentTerminationDate: date
    creditAgreementDate: date

class LoanTranche(BaseModel):
    transactionId: str
    capCommMasterId: str
    slDealNumber: str
    trancheId: str
    transactionState: str
    trancheStatusName: str
    trancheName: str
    totalSize: float
    gsSize: float
    fttDate: date
    trancheTypeName: str
    pricedDate: date
    announcedDate: date
    slTrancheId: str

class LoanTrancheExtd(BaseModel):
    transactionId: str
    transactionState: str
    trancheId: str
    projectName: str
    creditAgreementName: str
    masterTrancheId: str
    trancheType: str
    nativeCurrency: str
    gsCommitmentNative: str
    primeFacilityId: int
    approvedCreditHoldNative: float
    committeeApprovedCommitmentNative: float
    approvedRelationshipHoldNative: float
    gsBankApprovedCommitmentNative: float
    gsibApprovedCommitmentNative: float
    gsibApprovedHoldNative: float
    gsBankApprovedHoldNative: float
    gsRole: str
    interestRateMarginBps: float
    priceFlexBps: float
    oid: float
    accountingTreatment: str
    originalPurpose: str
    anticipatedFronting: str
    termLoanFlex: float
    materialChangesForLeveragedLoan: str
    negChangesToMaterialCondPrecedents: str
    strategy: str
    investmentSource: str
    expectedClosingDate: str
    issuerId: int
    maturityTenor: int
    maturityTenorPeriod: str
    seniority: str
    commitmentDate: datetime
    commitmentLength: str
    commitmentLengthPeriod: str
    commitmentTypeCode: str
    lendingDesignation: str
    creditRatingIcr: str
    creditRatingIcrNumeric: str
    doubleSigningDate: datetime
    refinancedTranches: str

class LoanTransaction(BaseModel):
    transactionId: str
    transactionState: str
    transactionType: str
    transactionSubType: str
    transactionPurpose: str
    masterId: str
    obligorId: int
    sponsorId: int
    projectName: str
    stateDate: datetime
    treeFinancing: str

class Order(BaseModel):
    orderId: str
    status: str
    salesPerson: str
    type: str
    overridePrice: str
    buySell: str
    overrideFirmAccount: str
    overrideTradeDate: date
    counterPartyAccount: str
    createdDate: date
    lastUpdateDate: date
    version: int
    overrideTransferType: str
    currency: str
    loanAssociation: str
    counterpartyDisplay: str
    assocSyndMemberId: int
    coverageBank: str
    allocation: str
    investor: Investor

class OrderStep(BaseModel):
    orderStepId: int
    orderId: int
    demand: int
    allocation: int
    repComment: str

class SyndicateMember(BaseModel):
    syndicateMemberId: str
    trancheId: str
    role: str
    alias: str
    underwritingAmount: float
    active: bool
    lastUpdateDate: str
    createdDate: str
    version: str
    firmAccounts: str

class TrancheBookingInfo(BaseModel):
    trancheBookingInfoId: str
    role: str
    tradername: str
    transferType: str
    initialBuyPrice: str
    sellDownDeskPrice: str
    firmAccount: str
    salesCredit: str
    lastUpdateDate: str
    createdDate: str
    version: str