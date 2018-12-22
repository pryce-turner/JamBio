from django.db import models

class ExecutionStats(models.Model):
    wo_id = models.CharField(max_length=20)
    website_order_id = models.CharField(max_length=20, default='0')

    FASTQC  = 'FQC'
    MULTIQC = 'MQC'
    QD      = 'QD'
    ANALYSIS_TYPE = (
        (FASTQC,  'FastQC'),
        (MULTIQC, 'MultiQC'),
        (QD,      'Enqueing')
    )
    analysis_type = models.CharField(
        max_length=10,
        choices=ANALYSIS_TYPE,
        default=FASTQC,
    )
    exec_date = models.DateTimeField()
    EXEC_STATUS = (
        ('INIT', 'Initial State'),
        ('ENQD', 'Enqueued'),
        ('OK',   'OK'),
        ('FAIL', 'Fail')
    )
    exec_status = models.CharField(
        max_length=4,
        choices=EXEC_STATUS,
        default='INIT',
    )
    details = models.CharField(max_length=256, null=True)
    
    def __str__(self):
        return 'WO: ' + self.wo_id
