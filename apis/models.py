from django.db import models


class DemoTable(models.Model):
    record_id = models.CharField(max_length=120, primary_key=True)
    record_name = models.CharField(
        max_length=120, verbose_name="Record Name"
    )

    class Meta:
        verbose_name = "Demo Table"
        verbose_name_plural = "Demo Table"
        db_table = "demo_table"

    def __str__(self):
        return f"{self.record_name}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if is_new:
            rec_name = self.record_name
            self.record_id = ''.join(
                char for char in rec_name.lower() if char.isalnum()
            )
        super().save(*args, **kwargs)
