TAXATION_OSN = 'osn'
TAXATION_USN_INCOME = 'usn_income'
TAXATION_USN_INCOME_OUTCOME = 'usn_income_outcome'
TAXATION_ENVD = 'envd'
TAXATION_ESN = 'esn'
TAXATION_PATENT = 'patent'

TAXATIONS = (
    (TAXATION_OSN, 'общая СН'),
    (TAXATION_USN_INCOME, 'упрощенная СН (доходы)'),
    (TAXATION_USN_INCOME_OUTCOME, 'упрощенная СН (доходы минус расходы)'),
    (TAXATION_ENVD, 'единый налог на вмененный доход'),
    (TAXATION_ESN, 'единый сельскохозяйственный налог'),
    (TAXATION_PATENT, 'патентная СН'),
)

TAX_ITEM_NONE = 'none'
TAX_ITEM_VAT0 = 'vat0'
TAX_ITEM_VAT10 = 'vat10'
TAX_ITEM_VAT18 = 'vat18'
TAX_ITEM_VAT110 = 'vat110'
TAX_ITEM_VAT118 = 'vat118'

TAXES = (
    (TAX_ITEM_NONE, 'без НДС'),
    (TAX_ITEM_VAT0, 'НДС по ставке 0%'),
    (TAX_ITEM_VAT10, 'НДС чека по ставке 10%'),
    (TAX_ITEM_VAT18, 'НДС чека по ставке 18%'),
    (TAX_ITEM_VAT110, 'НДС чека по расчетной ставке 10/110'),
    (TAX_ITEM_VAT118, 'НДС чека по расчетной ставке 18/118'),
)


# le-francais.ru settings

COFFEE_CUPS = 'coffee_cups'
LESSON_TICKETS = 'tickets'
DONATIONS = 'donations'
CATEGORIES = (
    (COFFEE_CUPS, 'Чашки кофе'),
    (LESSON_TICKETS, 'Тикеты'),
    (DONATIONS, 'Пожертвования')
)
CATEGORIES_E_NAME = {
    COFFEE_CUPS: 'Coffee Cup',
    LESSON_TICKETS: 'Ticket',
    DONATIONS: 'Donation',
}
CATEGORIES_E_SKU_PREFIX = {
    COFFEE_CUPS: 'C',
    LESSON_TICKETS: 'T',
    DONATIONS: 'D'
}

PAYMENT_STATUS_NEW = 'NEW'
PAYMENT_STATUS_FORM_SHOWED = 'FORM_SHOWED'
PAYMENT_STATUS_DEADLINE_EXPIRED = 'DEADLINE_EXPIRED'
PAYMENT_STATUS_CANCELED = 'CANCELED'
PAYMENT_STATUS_PREAUTHORIZING = 'PREAUTHORIZING'
PAYMENT_STATUS_AUTHORIZING = 'AUTHORIZING'
PAYMENT_STATUS_AUTHORIZED = 'AUTHORIZED'
PAYMENT_STATUS_AUTH_FAIL = 'AUTH_FAIL'
PAYMENT_STATUS_REJECTED = 'REJECTED'
PAYMENT_STATUS_3DS_CHECKING = '3DS_CHECKING'
PAYMENT_STATUS_3DS_CHECKED = '3DS_CHECKED'
PAYMENT_STATUS_REVERSING = 'REVERSING'
PAYMENT_STATUS_PARTIAL_REVERSED = 'PARTIAL_REVERSED'
PAYMENT_STATUS_REVERSED = 'REVERSED'
PAYMENT_STATUS_CONFIRMING = 'CONFIRMING'
PAYMENT_STATUS_CONFIRMED = 'CONFIRMED'
PAYMENT_STATUS_REFUNDING = 'REFUNDING'
PAYMENT_STATUS_PARTIAL_REFUNDED = 'PARTIAL_REFUNDED'
PAYMENT_STATUS_REFUNDED = 'REFUNDED'

PAYMENT_STATUS_CHOICES = [
    (PAYMENT_STATUS_NEW, 'NEW'),
    (PAYMENT_STATUS_FORM_SHOWED, 'FORM_SHOWED'),
    (PAYMENT_STATUS_DEADLINE_EXPIRED, 'DEADLINE_EXPIRED'),
    (PAYMENT_STATUS_CANCELED, 'CANCELED'),
    (PAYMENT_STATUS_PREAUTHORIZING, 'PREAUTHORIZING'),
    (PAYMENT_STATUS_AUTHORIZING, 'AUTHORIZING'),
    (PAYMENT_STATUS_AUTHORIZED, 'AUTHORIZED'),
    (PAYMENT_STATUS_AUTH_FAIL, 'AUTH_FAIL'),
    (PAYMENT_STATUS_REJECTED, 'REJECTED'),
    (PAYMENT_STATUS_3DS_CHECKING, '3DS_CHECKING'),
    (PAYMENT_STATUS_3DS_CHECKED, '3DS_CHECKED'),
    (PAYMENT_STATUS_REVERSING, 'REVERSING'),
    (PAYMENT_STATUS_PARTIAL_REVERSED, 'PARTIAL_REVERSED'),
    (PAYMENT_STATUS_REVERSED, 'REVERSED'),
    (PAYMENT_STATUS_CONFIRMING, 'CONFIRMING'),
    (PAYMENT_STATUS_CONFIRMED, 'CONFIRMED'),
    (PAYMENT_STATUS_REFUNDING, 'REFUNDING'),
    (PAYMENT_STATUS_PARTIAL_REFUNDED, 'PARTIAL_REFUNDED'),
    (PAYMENT_STATUS_REFUNDED, 'REFUNDED')
]

PAYMENT_PAYED_STATUSES = [PAYMENT_STATUS_CONFIRMED,
                          PAYMENT_STATUS_AUTHORIZED]
