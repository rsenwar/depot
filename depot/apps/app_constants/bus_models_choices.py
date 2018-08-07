"""Bus Model choices."""

STATUS_CHOICES = (
    ('new', 'new'),
    ('to deliver', 'to deliver'),
    ('charged', 'charged'),
    ('issue', 'issue'),
    ('pending','pending'),
    ('to refund','to refund'),
    ('refunded','refunded'),
    ('to cancel','to cancel'),
    ('to check', 'to check'),
    ('operator cancelled', 'operator cancelled'),
    ('op service issue','operator service issue')
)

BE_CHOICES = (
    ('1' , 'Seat not available'),
    ('2' , 'Customer already booked'),
    ('3' , 'Same bus not available'),
    ('4' , 'Already booked with goibibo'),
    ('5' , 'Other'),
    ('6' , 'Retry Flow Booking')
)


BE_MAP = {
    '1': 'Seat not available',
    '2': 'Customer already booked',
    '3': 'Same bus not available',
    '4': 'Already booked with goibibo',
    '5': 'Other',
    '6': 'Retry Flow Booking'
}

CANCEL_CHOICES = (
    ('to cancel' , 'to cancel'),
    ('issue','issue'),
    ('refunded','refunded'),
    ('pending','pending'),
    ('to refund','to refund'),
    ('to check','to check'),
    ('operator cancelled','operator cancelled'),
    ('refunded not cancelled', 'refunded not cancelled'),
    ('operator not cancelled', 'operator not cancelled'),
    ('op service issue', 'operator service issue'),
    ('allow refund','allow refund')
)
REASON_CHOICES = (('0', 'Unable to Cancel Online'),
                      ('2', 'Bus cancelled by operator'),
                      ('5', 'Normal Cancellation'),
                      ('6', 'Less than 8 hours'),
                      ('7', 'API Failure'),
                      ('8', 'Not cancelled by operator'),
                      ('4', 'Operator service issue')
)

ENV_CHOICES = (
    (1, 'dev'),
    (2, 'prod'),
    (3, 'prodpp'),
    (4, 'pp')
)




