from django.db import models
from django.contrib.auth.models import User
from treebeard.al_tree import AL_Node


# Create your models here.
class Account(models.Model):
    acctCd = models.CharField(max_length=200, blank=False, default='ABC', primary_key=True, unique=True)
    shortName = models.CharField(max_length=50, blank=False, default='ABC')
    cashSegregated = models.FloatField()
    cashUnSegregated = models.FloatField()
    totCash = models.FloatField()

    def __str__(self):
        return self.shortName

    class Meta:
        ordering = ('shortName',)


class AccountManager(models.Manager):
    def get_by_natural_key(self, acctFilterName):
        return self.get(acctFilterName=acctFilterName)


class AccountFilters(models.Model):
    objects = AccountManager()

    acctFilterName = models.CharField(max_length=200)
    accountName = models.ManyToManyField(Account)
    created_by = models.ForeignKey(User, related_name='%(class)s_requests_created', default='1')
    edited_by = models.ForeignKey(User, related_name='%(class)s_requests_edited', default='1')
    createDate = models.DateTimeField(auto_now_add=True)
    updateDate = models.DateTimeField(auto_now=True)

    def natural_key(self):
        return (self.acctFilterName)

    def __unicode__(self):
        return self.acctFilterName


class NewRebalance(models.Model):
    type = models.TextField()
    name = models.CharField(max_length=200, blank=False, default='')
    action = models.TextField()
    adjustCash = models.BooleanField(default=False)
    adjustWeightDuringRebal = models.BooleanField(default=False)
    excludePendingTrades = models.BooleanField(default=False)
    reviewSwapSale = models.BooleanField(default=False)
    adjustCashDuringRebal = models.BooleanField(default=False)
    createDate = models.DateTimeField(auto_now_add=True)
    updateDate = models.DateTimeField(auto_now=True)
    FIFO = 'FIFO'
    LIFO = 'LIFO'
    AVGCOST = 'AVGCOST'

    taxLotAlgoChoices = (
        (FIFO, 'FIFO'),
        (LIFO, 'LIFO'),
        (AVGCOST, 'Average Cost'),
    )

    taxLotAlgo = models.CharField(choices=taxLotAlgoChoices, default=FIFO, max_length=80)
    accounts = models.ForeignKey(Account, default='ABC')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('createDate',)


class ClassificationManager(models.Manager):
    def get_by_natural_key(self, classificationName):
        return self.get(classificationName=classificationName)


class ClassificationNames(AL_Node):
    objects = ClassificationManager()
    classificationLevel = models.IntegerField(null=True)
    classificationName = models.CharField(max_length=100, null=True)
    parent = models.ForeignKey('self', null=True, related_name='children_set', db_index=True)
    node_order_by = ['classificationName', 'desc', 'source']
    hasChildNode = models.NullBooleanField(default=False)

    def natural_key(self):
        return (self.classificationName)

    def __unicode__(self):
        return self.classificationName


class Countries(models.Model):
    cntry_cd = models.CharField(max_length=100, null=True)
    cntry_name = models.CharField(max_length=1000)
    iso_cntry_cd = models.CharField(max_length=50)


class Currencies(models.Model):
    currencyCd = models.CharField(max_length=100, null=True)
    currencyName = models.CharField(max_length=100, null=True)
    calc_precision = models.FloatField(null=True)


class AllocationModelManager(models.Manager):
    def get_by_natural_key(self, modelName):
        return self.get(modelName=modelName)


class Exchanges(models.Model):
    exch_cd = models.CharField(max_length=200, unique=True)
    exchange = models.CharField(max_length=1000)
    cntry_cd = models.ForeignKey(Countries)
    exch_or_otc = models.CharField(max_length=5)
    iso_exch_cd = models.CharField(max_length=10)
    tz_region = models.CharField(max_length=10)
    open_time = models.TimeField(null=True)
    mid_open_time = models.TimeField(null=True)
    mid_close_time = models.TimeField(null=True)
    cutoff_time = models.TimeField(null=True)
    close_time = models.TimeField(null=True)


class AllocationModels(models.Model):
    objects = AllocationModelManager()

    # id = models.AutoField(primary_key=True)
    modelName = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(User, related_name='%(class)s_requests_created', default='1')
    edited_by = models.ForeignKey(User, related_name='%(class)s_requests_edited', default='1')

    def natural_key(self):
        return (self.modelName)

    class Meta:
        ordering = ['modelName']


class AllocationNodes(models.Model):
    allocationModel = models.ForeignKey(AllocationModels, related_name='allocationNodes')
    classificationName = models.ForeignKey(ClassificationNames, related_name='classificationNames')
    level = models.IntegerField()
    dependentNode = models.CharField(max_length=300, null=True)

    def natural_key(self):
        return (self.allocationModel.natural_key() + self.classificationName.natural_key())

    natural_key.dependencies = ['equity.AllocationModel', 'equity.ClassificationNames']


class SecurityType(models.Model):
    secTypCd = models.CharField(primary_key=True, max_length=100)
    secName = models.CharField(max_length=200)


class Identity(models.Model):
    type = models.CharField(max_length=20)
    value = models.CharField(max_length=20)


class Security(models.Model):

    secId = models.IntegerField(primary_key=True)
    extSecId = models.CharField(max_length=100, null=True)
    secName = models.CharField(max_length=100, blank=False)
    shortName = models.CharField(max_length=100, null=True)
    secType = models.ForeignKey(SecurityType)
    issueState = models.CharField(max_length=100, null=True)
    issueCountry = models.ForeignKey(Countries)
    issueDate = models.DateField
    locCurrencyCd = models.CharField(max_length=20)
    crossCurrencyCd = models.CharField(max_length=20)
    listExchCd = models.CharField(max_length=20)
    baseCurrency = models.CharField(max_length=5, default='USD')
    mktPrice = models.FloatField()
    amtIssued = models.FloatField()
    amtOutstanding = models.FloatField()
    couponRate = models.FloatField()
    ticker = models.CharField(max_length=100, null=True)
    isin = models.CharField(max_length=100, null=True)
    sedol = models.CharField(max_length=100, null=True)
    cusip = models.CharField(max_length=100, null=True)
    RIC = models.CharField
    valoran = models.CharField(max_length=100, null=True)
    avgLife = models.DateField
    matureDate = models.DateField
    callDate = models.DateField
    putDate = models.DateField
    nextCouponDate = models.DateField
    strikePrice = models.FloatField()
    duration = models.FloatField
    expireDate = models.DateField
    fedTaxable = models.DateField
    privPlacement = models.BooleanField
    Yield = models.FloatField
    spread = models.FloatField
    wghtedAvg = models.FloatField
    preferredRate = models.FloatField
    firstExerciseDate = models.DateField
    lastModifyBy = models.ForeignKey(User)
    createDate = models.DateTimeField(auto_created=True)
    lastModifyDate = models.DateTimeField(auto_now_add=True)
    cnvrtRatio = models.FloatField
    comments = models.CharField(max_length=100, null=True)
    benchmarkSecurity = models.CharField(max_length=100, null=True)
    dayBasis = models.CharField
    putNoticeMonth = models.IntegerField
    putFrequency = models.FloatField
    couponPaymentDay = models.CharField
    couponPaymentAmt = models.FloatField
    firstPaymentDate = models.DateField
    lastPaymentDate = models.DateField
    prevPaymentDate = models.DateField
    paymentFrequency = models.CharField
    optionAdjSpread = models.FloatField
    modifiedDuration = models.FloatField
    accrualType = models.CharField
    defaultDate = models.DateField
    outOfDefaultDate = models.DateField
    convexity = models.FloatField
    interestType = models.CharField
    yieldToMature = models.FloatField
    yieldToWorstCall = models.FloatField
    yieldToWorstPut = models.FloatField
    WAC = models.FloatField
    WAM = models.FloatField
    prePayRate = models.FloatField
    delayDays = models.FloatField
    factor = models.FloatField
    factorDate = models.DateField
    mortgageYield = models.FloatField
    avgLifeDate = models.DateField
    poolNumber = models.CharField
    prepayFloor = models.FloatField
    prepayCap = models.CharField
    prepayCollar = models.FloatField
    prepayCollarUpper = models.FloatField
    prepayCollarLower = models.FloatField
    nextResetDate = models.FloatField
    nextSinkDate = models.DateField
    sinkPercent = models.FloatField
    convertPrice = models.FloatField
    convertStartDate = models.DateField
    convertEndDate = models.DateField
    resetDay = models.DateField
    eps = models.FloatField
    beta = models.FloatField
    peRatio = models.FloatField
    annualDividend = models.FloatField
    divCurrency = models.CharField(max_length=100, null=True)
    contractSize = models.FloatField
    lotSize = models.FloatField
    isERISA = models.BooleanField
    exDivDate = models.DateField
    marketCap = models.FloatField
    effectiveDuration = models.FloatField
    effectiveDate = models.DateField
    effectiveYield = models.FloatField
    effectiveModDuration = models.FloatField
    effectiveConvexity = models.FloatField
    interestPercent = models.FloatField
    countryOfRisk = models.CharField(max_length=100, null=True)
    recordVersion = models.IntegerField()

    def __unicode__(self):
        return self.secName


class SecurityClassification(models.Model):
    secId = models.ForeignKey(Security)
    classification = models.ForeignKey(ClassificationNames)


class TaxLot(models.Model):
    extTaxLotId = models.CharField(max_length=100, null=True)
    secId = models.ForeignKey(Security)
    acctCd = models.ForeignKey(Account)
    longOrShort = (('L', 'Long'), ('S', 'Short'))
    tradeDate = models.DateField()
    settleDate = models.DateField()
    qty = models.FloatField()
    costBaseAmount = models.FloatField()
    incBaseAmount = models.FloatField()
    unitBaseAmout = models.FloatField()
    qtyFactor = models.FloatField  # Factor for converting from q*p => Amt = (q*p)*factor


class Position(models.Model):
    acctCd = models.ForeignKey(Account)  # Account Code	Required	The account that holds this position.
    baseAcctCrncy = models.CharField(max_length=5, blank=False,
                                     default='USD')  # BAC	Required	Base account currency for this account.
    secId = models.ForeignKey(Security)  # Security ID	Required	Security identifier for this position.
    baseAcctCrncy = models.CharField(max_length=5, blank=False,
                                     default='USD')  # Currency	Required	Pricing/Settlement currency for this position.
    quantity = models.FloatField(
        blank=False)  # Quantity	Required	Start of Day quantity for this holding. If negative, this indicates a short position.
    mktVal = models.FloatField()  # Market Value	Required	The Start of Day market value of this holding.
    pledgedQty = models.FloatField()  # Pledged Qty	Optional	Quantity of the security that is pledged as collateral.
    segQty = models.FloatField()  # Segregated Qty	Optional	Quantity of the security to be segregated from trading.
    origCost = models.FloatField()  # Original Cost	Optional	Original cost of this position.
    origFace = models.FloatField()  # Original Face	Optional	Original face value of this position.


class RebalanceParameters(models.Model):
    rebalanceName = models.CharField(max_length=100, unique=True)
    saleType = models.CharField(max_length=15)
    buySell = models.CharField(max_length=5)
    reviewCurrentSale = models.BooleanField(default=False)
    adjustCashAfterRebal = models.BooleanField(default=False)
    adjustWgtAfterRebal = models.BooleanField(default=False)
    taxLots = models.CharField(max_length=100, null=True)


class AccountParameters(models.Model):
    acctFilterName = models.ForeignKey(AccountFilters)
    excludeClassification = models.ManyToManyField(ClassificationNames)
    tradingCash = models.FloatField()

    def __unicode__(self):
        return self.Name


class SecuritySelectionModels(models.Model):
    securitySelectionModelName = models.CharField(max_length=100, unique=True)
    classificationNames = models.ManyToManyField(ClassificationNames)

    userCreatedModel = models.TextField()

    def __unicode__(self):
        return self.securitySelectionModelName

    def natural_key(self):
        return self.securitySelectionModelName


class UserSecuritySelectionModel(AL_Node):

    parent = models.ForeignKey('self',
                               related_name='children_set',
                               null=True,
                               db_index=True)
    isSSMNameNode = models.BooleanField()
    SSM = models.ForeignKey(SecuritySelectionModels)
    classificationName = models.ForeignKey(ClassificationNames, null=True)
    tgtWeight = models.FloatField()
    currWeight = models.FloatField()
    hasChildNode = models.BooleanField()
    ext_model_id = models.IntegerField()

    node_order_by = ['ext_model_id']
